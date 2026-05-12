import axios from "axios";

const API = axios.create({
  baseURL: "https://hostelhub-jjvn.onrender.com",
});

export default API;