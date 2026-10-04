import express from "express";
import * as dotenv from "dotenv";
import cors from "cors";

import aiRoutes from "./routes/ai.routes.js";

dotenv.config();

const app = express();
const port = process.env.PORT || 5000;
app.use(cors());
app.use(express.json({ limit: "50mb" }));

app.use("/api/v1/ai", aiRoutes);

app.get("/", (req, res) => {
    res.status(200).send({ message: "Hello form AI Stitches"});
})

app.listen(port, () => console.log(`Server is running on port ${port}`))