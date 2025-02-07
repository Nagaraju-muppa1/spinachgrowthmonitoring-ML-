require("dotenv").config()
const userModel=require("../models/signup.model");
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt')
const {JWT_SCRETE_TOKEN}  =process.env

generateWebToken =(_id)=>{
    return  jwt.sign({ 
       id: _id },
       process.env.JWT_SCRETE_TOKEN,{
           expiresIn: '1d'
       });

}

const signup= async (req,res)=>{
    const { firstname, lastname, email, password} = req.body;
    try{
        const userExist = await userModel.findOne({email});
        if(userExist){
            return res.status(400).json({
               Success: false,
               message: "User email already exists."
            })
        }
        const hashpassword= await bcrypt.hash(password,10);

        const user= new userModel({
            firstname,
            lastname,
            email,
            password:hashpassword,
        })

        const savedUser =await user.save();

        const token =jwt.sign({email},JWT_SCRETE_TOKEN,{
            expiresIn:"1d"
        })
        res.status(200).json({
            message:"User Sucessfully registered", 
            token
        })
    }
    catch(error){
        console.log(error);
          return res.status(500).json({
            success: false,
            message: "Some error occurred while running. Contact your administrator.",
            
        })
    }
};

const signin=async(req,res)=>{
    const{
        email,
        password,
    }=req.query;
    console.log(email+" "+password);
    try{
        const user = await userModel.findOne({ email });
        const user_password= await userModel.findOne({ password});
         if(user ){
            var token = generateWebToken(user._id);
            return res.status(200).json({
                 success: true,
                 message: "uSer login Succesfully",
                 data:{user,
                     token: token}
             }) }
         else{
            return res.status(400).json({
                success:false,
                message:"User Email does not exist."
            })
         }

    }
    catch (error) {
        console.log(error);
        return res.status(500).json({
            success: false,
            message: "Some error occurred while running. Contact your administrator.",
        });
    }
}

module.exports={ signup, signin};