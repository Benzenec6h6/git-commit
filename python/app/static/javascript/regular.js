let cron=document.getElementById("import").textContent;
let sch=cron.split('\n');
sch.pop();
let i=1;

function set(schdule,area){
    let set_area=document.getElementById("content"+String(area));
    let min=set_area.querySelector("#min");
    let hour=set_area.querySelector("#hour");
    let day=set_area.querySelector("#day");
    let month=set_area.querySelector("#month");
    let week=set_area.querySelector("#week");
    let comp=set_area.querySelector("#company");
    t=schdule.split(' ');
    for(let i=0;i<min.length;i++){
        if(min[i].value==t[0]){
            min.options[i].selected=true;
        }
    }
    for(let i=0;i<hour.length;i++){
        if(hour[i].value==t[1]){
            hour.options[i].selected=true;
        }
    }
    for(let i=0;i<day.length;i++){
        if(day[i].value==t[2]){
            day.options[i].selected=true;
        }
    }
    for(let i=0;i<month.length;i++){
        if(month[i].value==t[3]){
            month.options[i].selected=true;
        }
    }
    for(let i=0;i<week.length;i++){
        if(week[i].value==t[4]){
            week.options[i].selected=true;
        }
    }
    for(let i=0;i<comp.length;i++){
        if(comp[i].value==t[6]){
            comp.options[i].selected=true;
        }
    }
}

function add(){
    //複製するエリア
    let content_area=document.getElementById("content0");
    //複製
    let clone=content_area.cloneNode(true);

    clone.id="content"+String(i);
    //付け足し
    let content=document.getElementById("content"+String(i-1));
    content.after(clone);
    i++;
}

function del(){
    const form_length = document.querySelectorAll("div").length;

    //フォームが1個なら処理終了
    if (form_length === 1) {
        return;

    } else {
        //div内の一番下の要素を取得
        let delete_form = document.getElementsByTagName("div");
        //要素を削除
        delete_form[i-1].remove();
        i--;
    }
}

for(let j=0;j<sch.length;j++){
    if(j<sch.length-1){
        add();
    }
    set(sch[j],j);
}
