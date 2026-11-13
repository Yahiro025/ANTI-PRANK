const fs=require('fs');
let h=fs.readFileSync('index.html','utf8');
for(const f of ['model.js','app.js'])h=h.replace('<script src="'+f+'"></script>','<script>'+fs.readFileSync(f,'utf8')+'</script>');
h=h.replace('assets/bricolage.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/BricolageGrotesque%5Bopsz%2Cwdth%2Cwght%5D.ttf');
h=h.replace('</style>','html,body{background:transparent}.layout{min-height:0}.main{margin:0 auto}</style>');
console.log(JSON.stringify(h));
