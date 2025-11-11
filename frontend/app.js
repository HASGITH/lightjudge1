const API_BASE = "";
let tasks = [];
async function loadTasks(){
  try{
    const res = await fetch(API_BASE + "/tasks/");
    tasks = await res.json();
    const list = document.getElementById("taskList");
    const select = document.getElementById("problemSelect");
    list.innerHTML = ""; select.innerHTML = "";
    tasks.forEach(t=>{
      const item = document.createElement("div");
      item.className = "task-item";
      item.innerHTML = `<h4>${t.id}. ${t.title}</h4><p>${t.description.slice(0,150)}</p>`;
      item.onclick = ()=>selectTask(t.id);
      list.appendChild(item);

      const opt = document.createElement("option");
      opt.value = t.id; opt.textContent = `${t.id}. ${t.title}`;
      select.appendChild(opt);
    });
  }catch(e){console.error(e)}
}
function selectTask(id){
  const t = tasks.find(x=>x.id==id);
  document.getElementById("taskDesc").textContent = t.description;
  document.getElementById("problemSelect").value = id;
}
document.getElementById("fillExample").onclick = ()=>{
  document.getElementById("code").value = `#include <bits/stdc++.h>\nusing namespace std;\nint main(){ long long a,b; if(!(cin>>a>>b)) return 0; cout<<(a+b); }\n`;
};
async function loadLeaderboard(){
  try{
    const res = await fetch(API_BASE + "/leaderboard/");
    const data = await res.json();
    const list = document.getElementById("leaderboard");
    list.innerHTML = "";
    data.forEach(u=>{
      const li = document.createElement("li"); li.textContent = `${u.username}: ${u.solved_count}`;
      list.appendChild(li);
    });
  }catch(e){console.error(e)}
}
document.getElementById("submitBtn").onclick = async ()=>{
  const username = document.getElementById("username").value.trim();
  const problem_id = document.getElementById("problemSelect").value;
  const code = document.getElementById("code").value;
  if(!username){alert("Введите username");return}
  if(!problem_id){alert("Выберите задачу");return}
  const form = new FormData();
  form.append("username", username);
  form.append("problem_id", problem_id);
  const blob = new Blob([code], {type:"text/x-c++src"});
  form.append("code", blob, "solution.cpp");

  const progressBar = document.getElementById("progressBar");
  progressBar.style.width = "10%";
  document.getElementById("result").textContent = "Отправка...";
  try{
    const res = await fetch(API_BASE + "/submit/", {method:"POST", body: form});
    const data = await res.json();
    if(data.status === "success"){
      progressBar.style.width = "100%";
      document.getElementById("result").innerHTML = `Результат: <strong>${data.score}%</strong> (${data.passed}/${data.total})`;
    }else if(data.status === "compile_error"){
      progressBar.style.width = "0%";
      document.getElementById("result").innerHTML = `<span style="color:${'#dc2626'}">Ошибка компиляции</span><pre style="white-space:pre-wrap;color:var(--muted)">${data.message}</pre>`;
    }else{
      document.getElementById("result").textContent = JSON.stringify(data);
    }
  }catch(err){
    console.error(err);
    document.getElementById("result").textContent = "Ошибка сети при отправке";
  } finally{
    loadLeaderboard();
  }
};

loadTasks(); loadLeaderboard();
