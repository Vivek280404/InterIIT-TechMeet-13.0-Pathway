""" 
This file is used to create and add graphs and charts in the generated output by leveraging the 'imgbb' API key
functions:
    - gen_url : generates the URL for the image using the 'imgbb' API key
    - get_paths : gets the paths of the images from the assets folder
    - generate_chart : generates the chart based on the content of the markdown file
"""
from dotenv import load_dotenv
import logging
import os
import google.generativeai as genai
from langchain_experimental.utilities import PythonREPL
import requests
from langchain_openai import ChatOpenAI

load_dotenv('../../.env')
api_gemini = os.getenv("GEMINI_API_KEY_30")
api_img = os.getenv("IMGBB_API_KEY")
openai_api_key=os.getenv("OPEN_AI_API_KEY_30")
GPT4o_mini_GraphGen = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.2, model_kwargs={"top_p": 0.1})


def gen_url(image_paths):
    """
    Generates the URL for the image using the 'imgbb' API key.
    Args:
        image_paths (list): List of paths of the images.
    Returns:
        list: List of URLs of the images.
    """
    api_key = api_img  
    url = []
    for image_path in image_paths:

        # Open the image and prepare the file for upload
        with open(image_path, 'rb') as image_file:
            # Define the payload (data) for the API call
            data = {
                'key': api_key,  
                'expiration': '1000',  
            }
            
            files = {
                'image': image_file,  
            }
            
            # Make the POST request to upload the image
            response = requests.post('https://api.imgbb.com/1/upload', data=data, files=files)

        response_json = response.json()
        if response_json['success']:
            print("Image uploaded successfully!")
            # print(f"Image URL: {response_json['data']['url_viewer']}")
            print(f"Image URL (direct link): {response_json['data']['url']}")
            url.append(response_json['data']['url'])
        else:
            print("Image upload failed!")
            print(response_json)

    return url

def get_paths(response):
    assets_folder = os.path.join(os.getcwd(), 'assets')
    image_paths = []

    for file_name in os.listdir(assets_folder):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(assets_folder, file_name)
            image_paths.append(image_path)

    url = gen_url(image_paths)
    genai.configure(api_key=api_gemini)
    model = genai.GenerativeModel("gemini-1.5-flash")

    message = f"""SYSTEM: you are a helpful AI assistant. you have been given a markdown file. It has images embedded in it. You also have a list of URLs of various images mentioned in the markdown file.
    Your job is to only replace the links of the images with the corresponding URL given. Do not try to change anything else. Return only the full markdown file, without any code block. Only return plain text.
    HUMAN: Markdown : {response}, URLS : {url}"""

    ai_msg = model.generate_content(message)
    file_path = 'response-withCharts.md'
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(ai_msg.text)
    return ai_msg.text



def generate_chart(content: str) -> str:
    """
    Analyzes a markdown file's content, determines if a chart can be generated, updates the markdown file
    to include the chart, and generates the chart using AI-generated Python code.

    specify the path where the new md file will be saved and the path where the image will be saved
    Args:
        content (str): Content of the markdown file to analyze.

    Returns:
        str: 'Image Saved' if the chart is successfully generated and saved, or an error message otherwise.
    """

    messages = f"""SYSTEM: You are being given a markdown file with the content below. The markdown file contains data extracted from different sources. 
    Your job is to first analyse the data, and find if any kind of potential data visualization can be built for it.\
    If a chart can be built, assume that it is generated and stored in 'assets' folder, with the name of the image being directly related to the data it is presenting. 
    Instructions:

    1. Now simply change the markdown file to include the image at the appropriate place, by mentioning a link to it at the appropriate place. 
    2. Only add a link to include the image and properly define the path of the image in markdown format. Do not change the content at all. 
    3. Do not add charts everywhere. Only add charts if and only if enough data is available. Only create charts for numeric data. 
    4. Do not create a graph if in case one of the value is not present for a source. 
    5. Use various different types of graphs available in matplotlib. 
    6. Do not add a markdown code block in the beginning. 
    """

    '''completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": messages},
            {
                "role": "user",
                "content": f"{content}"
            }
        ]
    )

    response_text = completion.choices[0].message.content.strip()'''

    response_text = GPT4o_mini_GraphGen.invoke(f'''{messages}\n\n {content}''').content

    file_path = 'response-withCharts.md'
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(response_text)
    print("done")
    repl = PythonREPL()


    messages_new = f"""SYSTEM: You are given content of a markdown file. It contains places where images have been inserted. 
    Your job is to generate the required charts based on the images that have been inserted in the markdown. Make a graph for 
    all the statements which look like:

    ![Heading of Image](path/of/image.png)


    DO NOT GENERATE GRAPHS WHICH ARE NOT INSERTED IN THE MARKDOWN

    1. Use your tools to generate the chart.
    2. Use a non-interactive backend. For example, (matplotlib.use('Agg')). 
    3. Do not view the chart. This is to make sure we avoid this error: NSWindow should only be instantiated on the main thread! 
    4. Do not start Matplotlib GUI.
    5. Save the images in the 'assets' folder. 
    6. Must respond with code directly. 
    7. Do not try to make a code block. 
    8. Just output the python code in plain text.

    Code Guidelines:
    1. Always include
    import matplotlib
    matplotlib.use('Agg')

    Guidelines:
    1. Do not include the punctuations at the starting or end.
    2. Do not include any starter text or header.
    3. Create the required image directory. Assume that it does not exist. 
    4. Successfully save the images to the required directory.
    5. Only create graphs wherever path to the image is defined in the markdown file. If not present, do not create a graph.

    IMPORTANT NOTE: IF THERE ARE MULTIPLE IMAGES INSERTED IN THE MARKDOWN, MAKE A GRAPH CORRESPONDING TO EACH IMAGE INSERTED BASED ON THE DATA NEAR IT.
    WRITE THE CODE SUCH THAT ALL THE IMAGES ARE SAVED AS DIFFERENT IMAGES WITH DESIGNATED NAMES BY RUNNING THE SINGLE PYTHON SCRIPT.
    """

        
    '''completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": messages_new},
            {
                "role": "user",
                "content": f"{response}"
            }
        ]
    )

    response = completion.choices[0].message.content.strip()'''

    response = GPT4o_mini_GraphGen.invoke(f'''{messages_new}\n\n {response_text}''').content

    try:
        result = repl.run(response)
        logging.info(f"Execution Result: {result}")
        return get_paths(response_text)
    except Exception as e:
        logging.error(f"Failed to execute code. Error: {repr(e)}")
        return f"Error {e}"

  