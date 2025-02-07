const express=require('express');
const cors = require("cors");
const multer = require('multer');
const axios = require('axios');
const fs =require('fs');
require('dotenv').config();
const app= express();
app.use(cors());
const dbconn=require('./database/dbconn')
const port='8000'
app.use(express.json()); // Parse JSON payloads

// Multer Setup (for file uploads)
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Route to Upload Image
app.post("/process-image", upload.single("image"), async (req, res) => {
    try {
        const response = await axios.post("http://127.0.0.1:5001/upload", req.file.buffer, {
            headers: {
                "Content-Type": "image/jpeg",
            },
            responseType: "arraybuffer",
        });

        res.set("Content-Type", "image/jpeg");
        res.send(response.data);
    } catch (error) {
        res.status(500).json({ error: "Error processing image" });
    }
});


app.get('/',(req,res)=>{
    res.send("Hello Welcome");
})
app.use('/api',require('./routes/userSignup.route'));



app.listen(port,()=>{
    console.log(`Server running at http://localhost:${8000}/`)
})