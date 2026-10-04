import { proxy } from "valtio";

const state = proxy({
    intro: true,
    color: "#5755FE",
    isLogoTexture: true,
    isFullTexture: false,
    logoDecal: "./ai.webp",
    fullDecal: "ai.webp",
});

export default state;