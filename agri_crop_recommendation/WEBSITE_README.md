# 🌾 Farmer Crop Recommendation Website

## Visual, Clean, and Farmer-Friendly Interface

A beautiful, bilingual (Hindi/English) web interface for the Indian Farmer Crop Recommendation System.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### 2. Start the Website
```bash
python run_website.py
```

### 3. Open in Browser
```
http://localhost:8000
```

---

## 🎨 Features

### For Farmers
- ✅ **Bilingual Interface** - Hindi and English side-by-side
- ✅ **Simple Form** - Easy to fill with clear labels
- ✅ **Visual Results** - Color-coded scores and risk indicators
- ✅ **Detailed Information** - Expandable cards with more details
- ✅ **Mobile Friendly** - Works on phones and tablets
- ✅ **No Login Required** - Direct access to recommendations

### Visual Elements
- 🌾 **Green Theme** - Agricultural color scheme
- 📊 **Score Bars** - Visual representation of suitability
- 🎯 **Risk Badges** - Color-coded risk levels (Low/Moderate/High)
- 📱 **Responsive Design** - Adapts to all screen sizes
- 🔍 **Expandable Cards** - Show/hide additional details

---

## 📋 How to Use

### Step 1: Select Your District
Choose from 10 supported districts:
- Pune, Solapur, Nashik, Ahmednagar, Aurangabad
- Jalgaon, Sangli, Kolhapur, Satara, Latur

### Step 2: Specify Irrigation
- **None** - No irrigation available
- **Limited** - Drip/sprinkler irrigation
- **Full** - Canal/well irrigation

### Step 3: (Optional) Add Soil Information
- Soil texture (Clay, Loam, Sandy, etc.)
- Soil pH (4.0 - 9.0)
- Organic matter content
- Drainage quality

### Step 4: Get Recommendations
Click "Get Crop Recommendations" to see:
- Top 10 suitable crops
- Suitability scores (0-100)
- Water requirements
- Risk assessments
- Duration and other details

---

## 🎯 What You'll See

### Results Include:
1. **Region Information**
   - District name
   - Current season (Kharif/Rabi/Zaid)
   - Climate zone
   - Soil type

2. **Weather Forecast**
   - Expected temperature
   - Expected rainfall
   - Dry spell risk

3. **Crop Recommendations**
   - Ranked by suitability score
   - Visual score bars (green/orange/red)
   - Water requirements
   - Irrigation needs
   - Risk level badges
   - Drought tolerance
   - Regional suitability

---

## 📱 Screenshots

### Main Form
```
┌─────────────────────────────────────────┐
│  📝 Enter Your Information              │
│                                         │
│  📍 District: [Pune ▼]                 │
│  💧 Irrigation: [Limited ▼]            │
│  ⏱️ Planning: [90 days]                │
│                                         │
│  🌱 Soil Information (Optional)        │
│  Texture: [Loam ▼]  pH: [7.0]         │
│                                         │
│  [🔍 Get Recommendations]              │
└─────────────────────────────────────────┘
```

### Crop Card
```
┌─────────────────────────────────────────┐
│  1️⃣  Bajra (Pearl Millet)              │
│                                         │
│  Suitability Score: 85.0/100           │
│  ████████████████░░░░ (85%)            │
│                                         │
│  ⏱️ 75 days    💧 400mm water          │
│  🌧️ 450mm rain  💦 0mm irrigation      │
│                                         │
│  🟢 Low Risk: Suitable conditions      │
│                                         │
│  [More Details ▼]                      │
└─────────────────────────────────────────┘
```

---

## 🌐 API Endpoints

The website uses these API endpoints:

### GET /
- Main web interface

### GET /regions
- List all supported regions

### POST /recommend
- Get crop recommendations
- Request body: region, irrigation, soil (optional)

### GET /health
- Health check

### GET /docs
- Interactive API documentation (Swagger UI)

---

## 🎨 Color Scheme

### Score Colors
- 🟢 **Green (70-100)** - High suitability
- 🟠 **Orange (50-69)** - Medium suitability
- 🔴 **Red (0-49)** - Low suitability

### Risk Colors
- 🟢 **Green** - Low risk
- 🟡 **Yellow** - Moderate risk
- 🔴 **Red** - High risk

---

## 📂 File Structure

```
agri_crop_recommendation/
├── templates/
│   └── index.html          # Main web page
├── static/
│   ├── css/
│   │   └── style.css       # Styling
│   └── js/
│       └── app.js          # JavaScript logic
├── src/api/
│   └── app.py              # FastAPI backend
└── run_website.py          # Startup script
```

---

## 🔧 Customization

### Change Colors
Edit `static/css/style.css`:
```css
:root {
    --primary-green: #2d5016;
    --light-green: #4a7c2c;
    --accent-orange: #ff8c42;
}
```

### Add More Languages
Edit `templates/index.html` to add translations.

### Modify Layout
Edit `static/css/style.css` for responsive breakpoints.

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in run_website.py
port=8001  # Instead of 8000
```

### Static Files Not Loading
```bash
# Ensure directories exist
mkdir -p static/css static/js templates
```

### API Errors
```bash
# Check if backend is running
curl http://localhost:8000/health
```

---

## 📊 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 2GB minimum
- **Storage**: 500MB for data
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)

---

## 🌟 Features for Farmers

### Easy to Understand
- Simple language (Hindi + English)
- Visual indicators (colors, icons)
- Clear explanations

### Comprehensive Information
- Suitability scores
- Water requirements
- Risk assessments
- Duration estimates

### Practical Guidance
- Season-specific recommendations
- Irrigation considerations
- Soil compatibility
- Regional suitability

---

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the implementation summary
3. Test with the provided test scripts

---

## ✨ Future Enhancements

Potential additions:
- [ ] Crop images
- [ ] Market price information
- [ ] Pest/disease warnings
- [ ] Planting calendar
- [ ] Success stories
- [ ] Video tutorials
- [ ] SMS/WhatsApp integration
- [ ] Offline mode

---

**Status**: ✅ **Production Ready**  
**Languages**: Hindi + English  
**Regions**: 10 Indian Districts  
**Crops**: 15 Short-Duration Varieties
