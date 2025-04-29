import { createContext, useState } from "react";
import runChat from "../config/Gemini";

export const Context = createContext();

const ContextProvider = (props) => {
	const [input, setInput] = useState("");
	const [recentPrompt, setRecentPrompt] = useState("");
	const [prevPrompts, setPrevPrompts] = useState([]);
	const [prevResults, setPrevResults] = useState([]);  // Store responses for previous prompts
	const [showResults, setShowResults] = useState(false);
	const [loading, setLoading] = useState(false);
	const [resultData, setResultData] = useState("");

	const delayPara = (index, nextWord) => {
		setTimeout(function () {
			setResultData((prev) => prev + nextWord);
		}, 10 * index);
	};
    
    const newChat = () => {
        setLoading(false);
        setShowResults(false);
        setInput("");
        setResultData("");  // Clear the results when starting a new chat
    }

	const onRender = async (data) => {
		setResultData("");
        let response = data;
		
		try {
			let responseArray = response.split("**");
            let newResponse = "";
			for (let i = 0; i < responseArray.length; i++) {
				if (i === 0 || i % 2 !== 1) {
					newResponse += responseArray[i];
				} else {
					newResponse += "<b>" + responseArray[i] + "</b>";
				}
			}
			let newResponse2 = newResponse.split("*").join("<br/>");
			let newResponseArray = newResponse2.split("");
			for (let i = 0; i < newResponseArray.length; i++) {
				const nextWord = newResponseArray[i];
				delayPara(i, nextWord + "");
			}
		} catch (error) {
			console.error("Error while running chat:", error);
			// Handle error appropriately
		} finally {
			setLoading(false);
			setInput("");
		}
	};

	const loadPreviousResponse = (index) => {
		// Set the result data from previous results
		setResultData(prevResults[index]);
		setShowResults(true); // Ensure the result is displayed
	};

	const contextValue = {
		prevPrompts,
		setPrevPrompts,
		prevResults,
		setPrevResults,
		setRecentPrompt,
		setShowResults,
		setResultData,
		recentPrompt,
		input,
		onRender,
		setInput,
		showResults,
		setLoading,
		loading,
		resultData,
		newChat,
		loadPreviousResponse,  // Add this function to load previous response
	};

	return (
		<Context.Provider value={contextValue}>{props.children}</Context.Provider>
	);
};

export default ContextProvider;
