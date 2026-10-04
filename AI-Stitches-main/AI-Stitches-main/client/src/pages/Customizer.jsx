import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useSnapshot } from "valtio";

import state from "../store";
// import { download } from "../assets";
import { downloadCanvasToImage, reader } from "../config/helpers";
import { EditorTabs, FilterTabs, DecalTypes } from "../config/constants";
import { fadeAnimation, slideAnimation } from "../config/motion";
import { AIPicker, ColorPicker, CustomButton, FilePicker, Tab } from "../components";

const Customizer = () => {
    const snap = useSnapshot(state);

    const [file, setFile] = useState('');
    const [prompt, setPrompt] = useState('');
    const [generatingImg, setGeneratingImg] = useState(false);
    const [activeEditorTab, setActiveEditorTab] = useState('');
    const [activeFilterTab, setActiveFilterTab] = useState({
        logoShirt: true,
        stylishShirt: false,
    })

    // Show tab content depending on the active tab
    const generateTabContent = () => {
        switch (activeEditorTab) {
            case "colorpicker":
                return <ColorPicker />
            case "filepicker":
                return <FilePicker
                    file={file}
                    setFile={setFile}
                    readFile={readFile}
                />
            case "aipicker":
                return <AIPicker
                    prompt={prompt}
                    setPrompt={setPrompt}
                    generatingImg={generatingImg}
                    handleSubmit={handleSubmit}
                />
            default:
                return null;
        }
    }

    // Toggle the selected editor tab
    const toggleEditorTab = (tabName) => {
        setActiveEditorTab((prevTab) => (prevTab === tabName ? '' : tabName));
    }

    const handleSubmit = async (type) => {
        if (!prompt) return alert("Please enter a prompt!");
      
        try {
          setGeneratingImg(true);
          
          const stabilityApiKey = "sk-yQZNbmyx43aNaxG0EE9tXlhOLbY6Amhoa4xOLBj0odchbt4s";
          
          // Option 1: Use a proxy backend (recommended solution)
          // Create a simple backend route that forwards requests to Stability AI
          
          // This could be your existing backend endpoint with modified logic
          const response = await fetch("https://ai-stitches.onrender.com/api/v1/ai", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              prompt,
              apiKey: stabilityApiKey, // Pass the API key to your backend
              useStabilityAI: true // Flag to tell your backend to use Stability AI
            })
          });
      
          // Option 2: If you can't modify your backend, you can try using a CORS proxy
          // (Note: Not recommended for production, use only for testing)
          /*
          const response = await fetch("https://cors-anywhere.herokuapp.com/https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Accept": "application/json",
              "Authorization": `Bearer ${stabilityApiKey}`
            },
            body: JSON.stringify({
              text_prompts: [{ text: prompt, weight: 1.0 }],
              cfg_scale: 7,
              height: 512,
              width: 512,
              samples: 1,
              steps: 30,
            })
          });
          */
      
          const data = await response.json();
          
          // If using your existing backend
          if (data.photo) {
            handleDecals(type, `data:image/png;base64,${data.photo}`);
          } 
          // If directly using Stability AI response format (with proxy)
          else if (data.artifacts && data.artifacts.length > 0) {
            const imageBase64 = data.artifacts[0].base64;
            handleDecals(type, `data:image/png;base64,${imageBase64}`);
          } else {
            throw new Error("No image was generated");
          }
        } catch (error) {
          console.error("Error details:", error);
          alert(error.message || "Failed to generate image");
        } finally {
          setGeneratingImg(false);
          setActiveEditorTab("");
        }
      };
    const handleDecals = (type, result) => {
        const decalType = DecalTypes[type];

        state[decalType.stateProperty] = result;

        if (!activeFilterTab[decalType.filterTab]) {
            handleActiveFilterTab(decalType.filterTab)
        }
    }

    const handleActiveFilterTab = (tabName) => {
        switch (tabName) {
            case "logoShirt":
                state.isLogoTexture = !activeFilterTab[tabName];
                break;
            case "stylishShirt":
                state.isFullTexture = !activeFilterTab[tabName];
            break;
            default:
                state.isLogoTexture = true;
                state.isFullTexture = false;
        }

        // after setting the state, activeFilterTab is updated

        setActiveFilterTab((prevState) => {
            return {
                ...prevState,
                [tabName]: !prevState[tabName]
            }
        })
    }

    const readFile = (type) => {
        reader(file)
            .then((result) => {
                handleDecals(type, result);
                setActiveEditorTab("");
            })
    }

  return (
    <AnimatePresence>
        {!snap.intro && (
            <>
                <motion.div
                    key="custom"
                    className="absolute top-0 left-0 z-10"
                    {...slideAnimation("left")}
                >
                    <div className="flex items-center min-h-screen">
                        <div className="editortabs-container tabs">
                            {EditorTabs.map((tab) => (
                                <Tab
                                    key={tab.name}
                                    tab={tab}
                                    handleClick={() => toggleEditorTab(tab.name)}
                                    isActive={activeEditorTab === tab.name}
                                />
                            ))}
                            {generateTabContent()}
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    className="absolute z-10 top-5 right-5"
                    {...fadeAnimation}
                >
                    
                    <CustomButton
                        type="filled"
                        title="Go Back"
                        handleClick={() => state.intro = true}
                        customStyles="w-fit px-4 py-2.5 font-bold text-sm"
                     />
                     <h1 className="mt-10 p-2 bg-black rounded text-white">Fix Price:500Rs</h1>
                </motion.div>
                            
                <motion.div
                    className="filtertabs-container"
                    {...slideAnimation("up")}
                >
                    {FilterTabs.map((tab) => (
                        <Tab
                            key={tab.name}
                            tab={tab}
                            isFilterTab
                            isActiveTab={activeFilterTab[tab.name]}
                            handleClick={() => handleActiveFilterTab(tab.name)}
                        />
                    ))}

                    <button className='download-btn' onClick={downloadCanvasToImage}>
                        <h1>Buy</h1>
                        {/* <img
                            src={download}
                            alt='download_image'
                            className='w-3/5 h-3/5 object-contain'
                        /> */}
                    </button>
                </motion.div>
            </>
        )}
    </AnimatePresence>
  )
}

export default Customizer