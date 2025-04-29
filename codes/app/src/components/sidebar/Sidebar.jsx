import "./sidebar.css";
import { assets } from "../../assets/assets";
import { useContext, useState } from "react";
import { Context } from "../../context/Context";
import Viewer from "../file/fileSystem";


const Sidebar = () => {
	const [extended, setExtended] = useState(true);
	const { prevPrompts, prevResults, setRecentPrompt, newChat, socket, setSocket, setIsUpload, isUpload } = useContext(Context);
	const [isPopupVisible, setPopupVisible] = useState(false);
	const [isFilePopupVisible, setFilePopupVisible] = useState(false);

	const [formData, setFormData] = useState({
		GoogleDrive_ObjectId: '',
		File_Link: '',
		GEMINI_API_KEY_30: '',
		OPEN_AI_API_KEY_30: '',
		FINNHUB_API_KEY_30: '',
		GOOGLE_CSE_ID_30: '',
		TAVILY_API_KEY_30: '',
		GOOGLE_API_KEY_30: '',
		JINA_API_KEY_30: '',
		INDIAN_KANOON_API_KEY_30: '',
		jsonFile: null
	});

	// Function to close the popup
	const closePopup = () => {
		setPopupVisible(false);
		setFilePopupVisible(false);
		setIsUpload(false);
	};

	// Function to open the popup (optional if needed)
	const openPopup = () => {
		setPopupVisible(true);
	};

	const openFilePopup = () => {
		setFilePopupVisible(true);
	};

	const loadPreviousPrompt = async (prompt) => {
		alert(result)
		setRecentPrompt(prompt);

		await onRender(prompt);
	};


	// Handle input changes
	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData((prevData) => ({
			...prevData,
			[name]: value
		}));
	};

	const handleFileChange = (e) => {
		const { name, files } = e.target;

		// Ensure the file exists and is of type JSON
		if (files && files[0] && files[0].type === 'application/json') {
			const file = files[0];

			// Create a FileReader to read the file
			const reader = new FileReader();

			reader.onload = () => {
				try {
					// Parse the JSON data from the file
					const parsedData = JSON.parse(reader.result);

					// Set the parsed data into the formData
					setFormData((prevData) => ({
						...prevData,
						[name]: parsedData // Store parsed JSON data
					}));
				} catch (error) {
					console.error('Error parsing JSON:', error);
				}
			};

			// Read the file as text (string)
			reader.readAsText(file);
		} else {
			console.error('Please upload a valid JSON file');
		}
	};

	// Handle form submission
	const handleSubmit = (e) => {
		e.preventDefault();
		// You can now use the formData object
		console.log(formData);
		if (socket && socket.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify({ type: 'cred', formData }));
		}
		// Optionally, you can handle the formData (e.g., send it to an API or store it)
		closePopup();
	};

	return (
		<>
			<div className={`sidebar ${extended ? "extended" : "collapsed"}`}>
				<div className="top">
					<div className={`buttons ${extended ? "extended" : "collapsed"}`}>
						<img
							src={assets.menu_icon}
							className="menu"
							id="dash"
							title="Dashboard"
							alt="menu-icon"
							onClick={() => setExtended((prev) => !prev)}
						/>
						<img
							src={assets.edit_icon}
							className="new"
							id="new"
							alt="new-icon"
							title="New Chat"
							onClick={() => {
								newChat()
							}}
						/>
					</div>
				</div>

				<div className="recent">
					<p className="recent-title">Recent</p>
					{prevPrompts.slice().reverse().map((item, index) => {
						return (
							<div key={index} onClick={() => loadPreviousPrompt(item)} className="recent-entry">
								<img src={assets.message_icon} alt="" />
								<p>{item.slice(0, 10)}...</p>
							</div>
						);
					})}

				</div>
				<div className="bottom">
					<div className="bottom-item recent-entry" onClick={openFilePopup}>
						<img src={assets.history_icon}
							alt=""
							title="Files" />
						{extended ? <p>Files</p> : null}
					</div>
					<div className="bottom-item recent-entry" onClick={openPopup}>
						<img src={assets.setting_icon}
							alt=""
							title="Credentials"

						/>
						{extended ? <p>Credentials</p> : null}
					</div>
				</div>
			</div>
			{isPopupVisible && (
				<div className="popup">
					<div className="popup-overlay" onClick={closePopup}></div>
					<div className="popup-form">
						<h2>Credentials</h2>
						<form className="custom-form">
							<div>

								<label htmlFor="OPEN_AI_API_KEY_30">OpenAI API Key</label>
								<input
									type="text"
									id="OPEN_AI_API_KEY_30"
									name="OPEN_AI_API_KEY_30"
									value={formData.OPEN_AI_API_KEY_30}
									onChange={handleChange}
									placeholder="API key for OpenAI"
								/>

								<label htmlFor="GEMINI_API_KEY_30">Gemini API Key</label>
								<input
									type="text"
									id="GEMINI_API_KEY_30"
									name="GEMINI_API_KEY_30"
									value={formData.GEMINI_API_KEY_30}
									onChange={handleChange}
									placeholder="API key for Gemini"
								/>


								<label htmlFor="FINNHUB_API_KEY_30">Finnhub API Key</label>
								<input
									type="text"
									id="FINNHUB_API_KEY_30"
									name="FINNHUB_API_KEY_30"
									value={formData.FINNHUB_API_KEY_30}
									onChange={handleChange}
									placeholder="API key for Finnhub"
								/>

								<label htmlFor="TAVILY_API_KEY_30">Tavily API Key</label>
								<input
									type="text"
									id="TAVILY_API_KEY_30"
									name="TAVILY_API_KEY_30"
									value={formData.TAVILY_API_KEY_30}
									onChange={handleChange}
									placeholder="API key for Tavily"
								/>

								<label htmlFor="VOYAGE_API_KEY">Voyage API Key</label>
								<input
									type="text"
									id="VOYAGE_API_KEY"
									name="VOYAGE_API_KEY"
									value={formData.VOYAGE_API_KEY}
									onChange={handleChange}
									placeholder="API key for Voyage"
								/>

								<label htmlFor="JINA_API_KEY_30">Jina API Key</label>
								<input
									type="text"
									id="JINA_API_KEY_30"
									name="JINA_API_KEY_30"
									value={formData.JINA_API_KEY_30}
									onChange={handleChange}
									placeholder="API key for Jina"
								/>

								<label htmlFor="INDIAN_KANOON_API_KEY_30">Indian Kanoon API Key</label>
								<input
									type="text"
									id="INDIAN_KANOON_API_KEY_30"
									name="INDIAN_KANOON_API_KEY_30"
									value={formData.INDIAN_KANOON_API_KEY_30}
									onChange={handleChange}
									placeholder="API key for Indian Kanoon"
								/>
							</div>

							<button type="submit" onClick={handleSubmit}>Submit</button>
						</form>
					</div>
				</div>
			)}
			{isFilePopupVisible && (
				<>
					<div className="popup">
						<div className="popup-overlay" onClick={closePopup}></div>
						<div className="popup-form">
							<Viewer />
						</div>
					</div>
				</>
			)}
			{isUpload && (
				<>	
					<div className="popup">
						<div className="popup-overlay" onClick={closePopup}></div>
						<div className="popup-form" >
							<h2>File Uploaded Successfully</h2>
						</div>
					</div>
				</>
			)}
		</>
	);
};

export default Sidebar;
