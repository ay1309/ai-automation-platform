import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost:5678",
});

export default api;