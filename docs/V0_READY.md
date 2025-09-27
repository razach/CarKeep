# CarKeep API for v0.app - Ready to Use!

## 🚀 API Base URL
```
https://carkeep.onrender.com/api
```

## 🔑 Key Endpoints for v0

### Get All Data
```javascript
// Get all scenarios + baseline
fetch('https://carkeep.onrender.com/api/scenarios')

// Get calculated comparisons  
fetch('https://carkeep.onrender.com/api/comparison-results')

// Get just baseline data
fetch('https://carkeep.onrender.com/api/baseline')
```

### Example Response
```json
{
  "baseline": {
    "vehicle": {
      "name": "Acura RDX",
      "current_value": 21000,
      "values_3yr": [21000, 18900, 17000, 15300]
    },
    "current_loan": {
      "monthly_payment": 564.1,
      "principal_balance": 9909.95
    }
  },
  "scenarios": {
    "cpo_acura_mdx_loan": {
      "description": "Acura RDX vs CPO Acura MDX with loan financing",
      "scenario": {
        "type": "loan",
        "vehicle": {
          "name": "CPO Acura MDX", 
          "msrp": 45000
        },
        "financing": {
          "monthly_payment": 1073.47
        }
      }
    }
  }
}
```

## ✅ CORS & Security
- ✅ CORS enabled for `https://v0.app` and `https://*.v0.app`
- ✅ Rate limited (100 requests/minute)
- ✅ Security headers active
- ✅ No API key required

## 🎯 Quick Test
```bash
curl https://carkeep.onrender.com/api/scenarios
```

## 📋 v0 Integration Checklist
- [x] API deployed and working
- [x] CORS configured for v0.app
- [x] Documentation updated (no localhost references)
- [x] Security features active
- [ ] Generate v0 frontend components
- [ ] Test API integration in v0

**Ready for v0.app integration!** 🚀