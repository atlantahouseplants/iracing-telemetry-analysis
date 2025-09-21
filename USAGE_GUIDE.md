# 🏎️ How to Use Your iRacing Telemetry Coach

## 🚀 Quick Start (Web UI - Recommended)

### Step 1: Launch the Web Interface
**Double-click:** `start_ui.bat`

OR manually run:
```bash
cd "C:\Users\wallg\Downloads\telemetry-20250921T030956Z-1-002\telemetry\src"
python web_ui.py
```

### Step 2: Open Your Browser
Go to: **http://localhost:5000**

### Step 3: Start Asking Questions!
The web interface will show:
- 📊 **Your telemetry statistics** (sessions, tracks, cars, best lap)
- 💬 **Chat interface** to ask your AI coach questions
- 🎯 **Example questions** you can click to try

## 🎮 Example Questions to Try

### Performance Analysis
- "What's my fastest lap time?"
- "How consistent am I?"
- "What's my best performance at Road Atlanta?"

### Improvement Coaching
- "How can I improve at Road Atlanta?"
- "What should I work on with the Porsche 992?"
- "What are my weaknesses?"

### Session Statistics
- "How many sessions do I have?"
- "What tracks have I driven?"
- "What cars have I used?"

## 📁 Adding New Telemetry Files

1. **Copy your .ibt files** to: `C:\Users\wallg\Downloads\telemetry-20250921T030956Z-1-002\telemetry\`
2. **Refresh the web page** - it will automatically process new files
3. **Ask questions** about your new sessions!

## 💻 Alternative: Command Line Usage

### Quick Test
```bash
cd "C:\Users\wallg\Downloads\telemetry-20250921T030956Z-1-002\telemetry\src"
python test_system.py
```

### Interactive Chat Mode
```bash
cd "C:\Users\wallg\Downloads\telemetry-20250921T030956Z-1-002\telemetry\src"
python main.py
```

## 🔧 Current System Status

**✅ Working Features:**
- Automatic IBT file processing
- Performance analysis and insights
- Track and car-specific coaching advice
- Natural language question answering
- Web-based chat interface
- Session statistics and tracking

**📊 Your Current Data:**
- 2 telemetry sessions processed
- Tracks: Road Atlanta, Talladega
- Cars: Porsche 992 Cup, Toyota GR86
- Best lap: 88.670s

## 🎯 What Your AI Coach Can Tell You

### Performance Metrics
- Fastest lap times by track/car
- Consistency ratings (0-10 scale)
- Improvement trends during sessions
- Comparative performance analysis

### Coaching Insights
- **Road Atlanta**: Late braking into Turn 1, chicane momentum, elevation changes
- **Talladega**: Draft management, fuel economy, incident awareness
- **Porsche 992 Cup**: Precise inputs, late braking capability
- **Toyota GR86**: Balanced handling, consistent brake points

### Session Analysis
- Lap count and session duration
- Strengths to build upon
- Specific improvement areas
- Next session focus recommendations

## 🚨 Troubleshooting

### Web UI Won't Start
1. Make sure Python is installed
2. Try: `pip install flask`
3. Run: `cd src && python web_ui.py`

### No Data Showing
1. Make sure your .ibt files are in the main telemetry folder
2. Check the file names match the pattern: `car_track date time.ibt`
3. Refresh the web page to reprocess files

### Questions Not Working
1. Try the example questions first
2. Be specific about tracks/cars (e.g., "Road Atlanta", "Porsche 992")
3. Ask simpler questions if complex ones fail

## 🎮 Tips for Best Results

### File Organization
- Keep .ibt files in the main telemetry folder
- Use descriptive filenames from iRacing
- Don't rename the files after download

### Question Format
- Use full track names: "Road Atlanta" not "RA"
- Specify cars clearly: "Porsche 992" or "Toyota GR86"
- Ask one thing at a time for clearest answers

### Getting Better Insights
- Process multiple sessions for better analysis
- Ask about specific tracks/cars you want to improve
- Use the coaching advice for your next practice sessions

## 🚀 What's Next

The system is ready to grow with you:
- Add more .ibt files as you race
- Get increasingly personalized coaching advice
- Track your improvement over time
- Compare performance across different tracks and cars

**Start by double-clicking `start_ui.bat` and open http://localhost:5000 in your browser!**