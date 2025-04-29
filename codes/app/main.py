import asyncio
import websockets
import json

resp = '''### Can Nokia Acquire Apple?

Nokia acquiring Apple is a proposition that, at first glance, appears to be highly improbable due to several critical factors including financial disparity, strategic misalignment, regulatory challenges, and potential cultural and operational issues. This report delves deeply into each of these areas, providing a comprehensive analysis supported by relevant data, tables, and expert opinions.

#### 1. Financial Disparity

One of the most glaring hurdles in the way of Nokia acquiring Apple is the financial disparity between the two companies. 
[**gogole**](https://.google.com)
**Market Capitalization**: As of the latest data, Apple's market capitalization is approximately $3.55 trillion, making it one of the most valuable companies globally (Source: Yahoo Finance). In contrast, Nokia's market capitalization is about $22.65 billion (Source: Nokia Investor Relations). This positions Apple as over 160 times more valuable than Nokia, highlighting the financial infeasibility of such an acquisition. 

**Revenue Comparison**: Apple reported annual revenues of $383.3 billion in 2023, reflecting its dominant market position and strong financial performance (Source: MacroTrends). On the other hand, Nokia's annual revenue for the same period was $24.09 billion, showing a decline of 8.22% from the previous year (Source: YCharts). The revenue gap emphasizes the scale difference between the two companies.

| Company | Market Capitalization (in billions) | 2023 Annual Revenue (in billions) |
|---------|-------------------------------------|-----------------------------------|
| Apple   | $3,550                              | $383.3                            |
| Nokia   | $22.65                              | $24.09                            |

![Financial Comparison](https://i.ibb.co/7yMKjXd/financial-comparison.png)

**Debt-to-Equity Ratios**: Apple's debt-to-equity ratio is approximately 1.79 to 1.87, indicating that it uses a significant amount of debt in its capital structure (Source: YCharts). Nokia’s debt-to-equity ratio is reported as 0.20, suggesting a more conservative use of debt (Source: AlphaQuery). These financial metrics further illustrate the stark differences in financial strategies and capacities between the two companies.

#### 2. Strategic Misalignment

The strategic directions of Nokia and Apple are fundamentally different, posing another significant challenge to any potential acquisition.

**Business Focus and Market Positioning**: Apple is a leader in consumer electronics, with a strong emphasis on innovation and a robust ecosystem of devices, software, and services. It designs, manufactures, and markets popular products like the iPhone, iPad, and Mac computers, alongside services such as Apple Music and Apple TV+ (Source: Apple Official Website). Nokia, however, primarily operates in the telecommunications infrastructure sector, focusing on network equipment and services (Source: Nokia Official Website).

**Growth Trajectories**: Apple's growth has been characterized by its ability to innovate and capture significant market share in consumer electronics. It has consistently reported high profit margins and a strong return on equity (ROE) of 157.41%, showcasing effective management and profitability (Source: Finnhub API). Conversely, Nokia has faced challenges in maintaining its market position, with a much lower ROE of 4.49% and negative revenue growth in recent years (Source: Nokia Company Profile).

#### 3. Regulatory Challenges

The potential acquisition of Apple by Nokia would likely face considerable regulatory scrutiny, particularly due to antitrust concerns.

**Antitrust Regulations**: Both the U.S. Department of Justice and the European Union have been vigilant in scrutinizing large mergers and acquisitions to prevent anti-competitive practices. Apple's dominant position in the tech industry means that any acquisition attempt could be seen as limiting competition, potentially resulting in legal challenges and delays (Source: New York Times, Reuters).

**National Security Concerns**: The Committee on Foreign Investment in the United States (CFIUS) could also pose significant hurdles, especially if the acquisition involves foreign entities and impacts sensitive technologies or data (Source: Financial Times).

#### 4. Cultural and Operational Challenges

Beyond financial and regulatory issues, the cultural and operational integration of Nokia and Apple would pose substantial challenges.

**Cultural Differences**: Nokia's Finnish corporate culture values consensus and egalitarianism, whereas Apple's American culture is more competitive and individualistic. These differences could lead to friction and misunderstandings, as evidenced by the failure of similar cross-cultural mergers in the past (Source: Success Across Cultures).

**Operational Integration**: The integration of technological systems and organizational restructuring required for a merger of this magnitude could lead to significant operational disruptions. Historical data indicates that 50-70% of employees leave within the first year post-merger due to uncertainties, which could further hinder the success of such an acquisition (Source: MNA Community).

#### Conclusion

In conclusion, the prospect of Nokia acquiring Apple is fraught with significant challenges that make it an extremely unlikely scenario. The financial disparity between the two companies is vast, with Apple's market dominance and financial health far surpassing Nokia's capabilities. Strategic misalignment in their business models and market focuses further complicates the feasibility of such an acquisition.

Moreover, regulatory hurdles present formidable barriers, as any attempt to acquire Apple would likely attract intense scrutiny from antitrust regulators and national security bodies. Cultural and operational challenges add another layer of complexity, with potential integration issues threatening the success of any merger.

Given these factors, it is clear that Nokia acquiring Apple is not a feasible proposition at this time. Instead, Nokia may benefit more from focusing on strengthening its core business areas and exploring strategic partnerships or smaller acquisitions that align more closely with its market position and capabilities. For Apple, maintaining its strong market position and continuing its innovation-driven growth strategy remains paramount. 

In summary, while the idea of Nokia acquiring Apple is intriguing, the practical challenges are insurmountable given the current financial, strategic, regulatory, and cultural landscapes.'''
questions =['q1', '### Historical Context of Media Mergers', "qdjqwnjqwdnjwqkdnqwkjdnqwkjdn3"]


async def send(websocket):
    agents = [
        {"name": "order_hisqwerwetory", "response": "Analyzing osdfaaaaaadsffffffffffffrder history..."},
        {"name": "clicerewwkstream", "response": "Analyzing usersdf clizxcxxxxxxxxxxxxxxxxxxxxxxxxack patterns..."},
        {"name": "invewerwerntory", "response": "Cross-chfdffffffffffffffffffffffffffffffffassdfgdgfsdfgecking inventory status..."}
    ]
    await websocket.send(json.dumps({"type": "agents", "agents": agents}))

async def handle_connection(websocket):  # Removed unused 'path' parameter
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'query':
                print(f"Received query: {data['query']}")

                # Simulate agent analysis responses
                agents = [
                    {"name": "order_history", "response": "Analyjksfhjksdfjkhskjdgfhkszing order history..."},
                    {"name": "clickstream", "response": "Analyzing asdfhjkashfdjahsfkuser click patterns..."},
                    {"name": "inventory", "response": "Cross-checkasdjkfghjgfjhasgdfhjaging inventory status..."}
                ]
                await asyncio.sleep(2)
                with open('./ProcessLogs.md', 'a') as fp:
                    fp.write(str(agents))

                agents = [
                    {"name": "order_hsdfgsdistory", "response": "Analyjajkdfhjahfksfhjksdfjkhskjdgfhkszing order history..."},
                    {"name": "clasdfaickstream", "response": "Analyzing asdfhjkashfakjhdfjkahdfkjdjahsfkuser click patterns..."},
                    {"name": "inasdfventory", "response": "Cross-checkasdjkfghjgfjajkahfjkahfkhasgdfhjaging inventory status..."}
                ]
                
                # await websocket.send(json.dumps({"type": "agents", "agents": agents}))
                await asyncio.sleep(2)
                with open('./ProcessLogs.md', 'a') as fp:
                    fp.write(str(agents))
                # await send(websocket)

                # Simulate final bot response
                await asyncio.sleep(1)
                await websocket.send(json.dumps({"type": "response", "response": resp}))
                await asyncio.sleep(1)
                await websocket.send(json.dumps({"type": "questions", "questions": questions}))

    except websockets.exceptions.ConnectionClosed:
        print("Client connection closed")
    except Exception as e:
        print(f"Error handling connection: {e}")

async def main():
    print("WebSocket server starting on ws://0.0.0.0:8080")
    async with websockets.serve(handle_connection, "localhost", 8080):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown by user")