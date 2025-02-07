const mongoose=require('mongoose');
const userSchema=mongoose.Schema({
    firstname:{
        type:String,
        require:[true,"Please provide first name"],
        trim:true,
        min: 3,
        max:50
    },
    lastname:{
        type:String,
        require:[true,"Please provide last name"],
        trim:true,
        min: 3,
        max:50
    },
    email:{
        type:String,
        require:[true,"Please provide email"],
        trim:true,
        min:3,
        max:60
    },
    password:{
        type:String,
        require:true,
    }
},
{
    timestamps:true,
})

module.exports=mongoose.model("SingupUsers",userSchema);