<!DOCTYPE html>
<html>
<head>
<title>OptionGuru Hooriya PRO</title>

<style>
body { background:#0d1117; color:white; text-align:center; font-family:Arial; }

.card {
    margin:20px auto;
    padding:20px;
    width:320px;
    border-radius:10px;
    background:#161b22;
}

.signal {
    font-size:16px;
    margin-top:10px;
    line-height:1.6;
}
</style>
</head>

<body>

<h1>🚀 OptionGuru Hooriya (PRO AI)</h1>

<div class="card"><h2>NIFTY</h2><div id="nifty">Loading...</div></div>
<div class="card"><h2>BANKNIFTY</h2><div id="bank">Loading...</div></div>
<div class="card"><h2>FINNIFTY</h2><div id="fin">Loading...</div></div>
<div class="card"><h2>SENSEX</h2><div id="sensex">Loading...</div></div>

<script>
async function loadData(){

    let n = await fetch("/nifty").then(r=>r.json());
    let b = await fetch("/banknifty").then(r=>r.json());
    let f = await fetch("/finnifty").then(r=>r.json());
    let s = await fetch("/sensex").then(r=>r.json());

    function format(x){
        return x.signal + " | " + x.prediction +
        " | Entry: " + x.entry +
        " | SL: " + x.sl +
        " | Target: " + x.target;
    }

    document.getElementById("nifty").innerText = format(n);
    document.getElementById("bank").innerText = format(b);
    document.getElementById("fin").innerText = format(f);
    document.getElementById("sensex").innerText = format(s);
}

// ⏱ refresh 20 sec
setInterval(loadData, 20000);
loadData();
</script>

</body>
</html>
