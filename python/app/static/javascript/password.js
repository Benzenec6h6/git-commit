window.onload = function() {
    let name=document.getElementsByTagName("th");
    let category=document.getElementById("category");
    let before=document.getElementById("before");

    category.onchange = changeCategory;
}

function changeCategory() {

  let changedCategory = category.value;

  if (changedCategory == "証券会社" || changedCategory == "company") {

    setcomp();

  } else if (changedCategory == "ID") {

    setID();

  } else if(changedCategory == "password"){

    setpassword();

  }else{

    setsave();

  }

}

// 和食の選択肢を設定する

function setcomp() {
  //complist=document.getElementsByClassName("証券会社")
  complist=document.getElementsByClassName("company")
  //選択リスト初期化
  before.textContent = null;

  // 証券会社の選択
  let comp=[];
  for(let i=0;i<complist.length;i++){
    comp.push(complist[i].textContent);
  }

  for(let i=0;i<comp.length;i++) {

    let op = document.createElement("option");

    op.text = comp[i];

    before.appendChild(op);

  }
}


function setID() {
  listID=document.getElementsByClassName("ID")
  before.textContent = null;
  let IDlist=[];
  for(let i=0;i<listID.length;i++){
    IDlist.push(listID[i].textContent);
  }

  for(let i=0;i<IDlist.length;i++) {

    let op = document.createElement("option");

    op.text = IDlist[i];

    before.appendChild(op);

  }

}

function setpassword() {

  listpass=document.getElementsByClassName("password");

  before.textContent = null;

  let passlist=[];
  for(let i=0;i<listpass.length;i++){
    passlist.push(listpass[i].textContent);
  }

  for(let i=0;i<passlist.length;i++) {

    let op = document.createElement("option");

    op.text = passlist[i];

    before.appendChild(op);

  }

}

function setsave() {

  //listsave=document.getElementsByClassName("保存名");
  listsave=document.getElementsByClassName("savename");

  before.textContent = null;

  let savename=[];
  for(let i=0;i<listsave.length;i++){
    savename.push(listsave[i].textContent);
  }

  for(let i=0;i<savename.length;i++) {

    let op = document.createElement("option");

    op.text = savename[i];

    before.appendChild(op);

  }

}