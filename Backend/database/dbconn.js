const mongoose=require('mongoose');
const url=`mongodb+srv://nagarajumuppavaram2491:Rx6X2Mff0HSggQne@cluster0.s8zct.mongodb.net/demo_sample`

mongoose.connect(url)
 .then(()=>{ console.log("DB connected Successfully")})
 .catch((error)=>console.log("connection",error));
 
const dbConn=mongoose.connection
module.exports=dbConn;
