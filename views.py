# app/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from PIL import Image
import tensorflow as tf
from io import BytesIO
import json

from django.contrib.auth.decorators import login_required

from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Community,FarmerScheme
from .form import CommunityForm


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Load the model from the .h5 file
MODEL = tf.keras.models.load_model("app/templates/AiFieldMedic.h5", compile=False)


# Define the class names
CLASS_NAMES = [
 'Apple___Apple_scab',
 'Apple___Black_rot',
 'Apple___Cedar_apple_rust',
 'Apple___healthy',
 'Blueberry___healthy',
 'Cherry_(including_sour)___Powdery_mildew',
 'Cherry_(including_sour)___healthy',
 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
 'Corn_(maize)___Common_rust_',
 'Corn_(maize)___Northern_Leaf_Blight',
 'Corn_(maize)___healthy',
 'Grape___Black_rot',
 'Grape___Esca_(Black_Measles)',
 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
 'Grape___healthy',
 'Orange___Haunglongbing_(Citrus_greening)',
 'Peach___Bacterial_spot',
 'Peach___healthy',
 'Pepper,_bell___Bacterial_spot',
 'Pepper,_bell___healthy',
 'Potato___Early_blight',
 'Potato___Late_blight',
 'Potato___healthy',
 'Raspberry___healthy',
 'Soybean___healthy',
 'Squash___Powdery_mildew',
 'Strawberry___Leaf_scorch',
 'Strawberry___healthy',
 'Tomato___Bacterial_spot',
 'Tomato___Early_blight',
 'Tomato___Late_blight',
 'Tomato___Leaf_Mold',
 'Tomato___Septoria_leaf_spot',
 'Tomato___Spider_mites Two-spotted_spider_mite',
 'Tomato___Target_Spot',
 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
 'Tomato___Tomato_mosaic_virus',
 'Tomato___healthy'
]

# Define the tomato disease data directly in the views.py file
tomato_disease_data = {
    "Apple___Apple_scab": {
        "scientific_name": "Venturia inaequalis",
        "cause": "Fungal infection caused by Venturia inaequalis.",
        "symptoms": "Olive-green spots on leaves that turn brown and lead to leaf drop.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Dilute and spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and deters pests.",
                "notes": "Best applied in the early morning or late evening."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray as per product instructions.",
                "benefits": "Competes with harmful fungi, reducing their population.",
                "notes": "Effective preventively or at the first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Follow manufacturer's instructions; typically applied every 7-14 days.",
                "benefits": "Controls fungal diseases effectively.",
                "notes": "Avoid excessive use to prevent soil accumulation."
            }
        },
        "familiar_pesticides": ["Mancozeb", "Chlorothalonil"],
        "prevention": "Practice good orchard sanitation and prune affected branches."
    },

    "Apple___Black_rot": {
        "scientific_name": "Glomerella cingulata",
        "cause": "Fungal infection caused by Glomerella cingulata.",
        "symptoms": "Dark, sunken lesions on fruit and leaves.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal spores and repels insects.",
                "notes": "Apply in cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Apply as a foliar spray.",
                "benefits": "Reduces fungal population.",
                "notes": "Use preventively or at first sign of infection."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow label instructions for application.",
                "benefits": "Controls black rot effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Myclobutanil", "Azoxystrobin"],
        "prevention": "Remove infected fruit and maintain good air circulation."
    },

    "Apple___Cedar_apple_rust": {
        "scientific_name": "Gymnosporangium juniperi-virginianae",
        "cause": "Fungal infection caused by Gymnosporangium juniperi-virginianae.",
        "symptoms": "Yellow spots on leaves with orange spore masses on the underside.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Deters pests and suppresses fungal growth.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or when symptoms appear."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Apply every 7-10 days as per manufacturer's instructions.",
                "benefits": "Controls rust diseases effectively.",
                "notes": "Avoid overuse to protect beneficial microbes."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Mancozeb"],
        "prevention": "Practice crop rotation and remove cedar trees near apple orchards."
    },

    "Apple___healthy": {
        "status": "No disease present",
        "prevention": "Regularly monitor for pests, maintain good soil health."
    },

    "Blueberry___healthy": {
        "status": "No disease present",
        "prevention": "Maintain soil acidity, monitor for pests, and provide proper drainage."
    },

    "Cherry_(including_sour)___Powdery_mildew": {
        "scientific_name": "Podosphaera clandestina",
        "cause": "Fungal infection caused by Podosphaera clandestina.",
        "symptoms": "White powdery coating on leaves and fruit.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Dilute and spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and repels insects.",
                "notes": "Apply during cooler times of day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with the fungus, reducing its population.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow label instructions for application.",
                "benefits": "Controls powdery mildew effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Myclobutanil", "Sulfur"],
        "prevention": "Ensure good air circulation and avoid overhead watering."
    },

    "Cherry_(including_sour)___healthy": {
        "status": "No disease present",
        "prevention": "Maintain soil health, monitor for pests, and provide adequate spacing."
    },

    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot": {
        "scientific_name": "Cercospora zeae-maydis",
        "cause": "Fungal infection causing leaf spots.",
        "symptoms": "Grayish spots with yellow halos on leaves.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and deters pests.",
                "notes": "Apply in the early morning or late evening."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with the fungus, reducing its population.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Apply every 7-10 days as per manufacturer's instructions.",
                "benefits": "Controls gray leaf spot effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "prevention": "Practice crop rotation and remove infected plant debris."
    },

    "Corn_(maize)___Common_rust_": {
        "scientific_name": "Puccinia sorghi",
        "cause": "Fungal infection caused by Puccinia sorghi.",
        "symptoms": "Reddish-brown pustules on leaves.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses rust spores and repels pests.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Apply every 7-10 days as per manufacturer's instructions.",
                "benefits": "Controls common rust effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "prevention": "Rotate crops and remove infected plant debris."
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "scientific_name": "Exserohilum turcicum",
        "cause": "Fungal infection caused by Exserohilum turcicum.",
        "symptoms": "Long, grayish lesions on leaves.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal spores and deters pests.",
                "notes": "Apply in the morning or evening."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Apply every 7-10 days as per manufacturer's instructions.",
                "benefits": "Controls northern leaf blight effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "prevention": "Rotate crops and remove infected plant debris."
    },

    "Corn_(maize)___healthy": {
        "status": "No disease present",
        "prevention": "Practice crop rotation and monitor for pests."
    },

    "Grape___Black_rot": {
        "scientific_name": "Guignardia bidwellii",
        "cause": "Fungal infection caused by Guignardia bidwellii.",
        "symptoms": "Dark, circular spots on leaves and fruit.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and repels insects.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Controls black rot effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Mancozeb", "Myclobutanil"],
        "prevention": "Practice good vineyard management and remove infected fruit."
    },

    "Grape___Esca_(Black_Measles)": {
        "scientific_name": "Phaeomoniella chlamydospora",
        "cause": "Fungal infection caused by Phaeomoniella chlamydospora.",
        "symptoms": "Leaf yellowing, fruit shriveling, and black streaks in wood.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and deters pests.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow manufacturer's instructions for application.",
                "benefits": "Controls Esca effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Copper hydroxide", "Myclobutanil"],
        "prevention": "Ensure good drainage and avoid overwatering."
    },

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "scientific_name": "Isariopsis citricola",
        "cause": "Fungal infection caused by Isariopsis citricola.",
        "symptoms": "Dark, angular leaf spots.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and repels insects.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Controls leaf blight effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Mancozeb"],
        "prevention": "Practice good vineyard management and remove infected leaves."
    },

    "Grape___healthy": {
        "status": "No disease present",
        "prevention": "Maintain good vineyard practices and monitor for pests."
    },

    "Orange___Haunglongbing_(Citrus_greening)": {
        "scientific_name": "Candidatus Liberibacter asiaticus",
        "cause": "Bacterial infection caused by Candidatus Liberibacter asiaticus.",
        "symptoms": "Yellowing leaves, misshapen fruit, and dieback.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Repels pests and supports plant health.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a soil drench.",
                "benefits": "Helps in suppressing bacterial populations.",
                "notes": "Can be used preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Controls bacterial diseases effectively.",
                "notes": "Rotate products to prevent resistance."
            }
        },
        "familiar_pesticides": ["Streptomycin", "Copper hydroxide"],
        "prevention": "Maintain good tree health and monitor for pests."
    },

    "Peach___Bacterial_spot": {
        "scientific_name": "Xanthomonas arboricola pv. pruni",
        "cause": "Bacterial infection caused by Xanthomonas arboricola.",
        "symptoms": "Water-soaked spots on leaves, leading to leaf drop.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Disrupts the lifecycle of bacteria and deters pests.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful bacteria.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Inhibits the growth of bacteria.",
                "notes": "Avoid overuse to protect beneficial microbes."
            }
        },
        "familiar_pesticides": ["Copper sulfate", "Streptomycin"],
        "prevention": "Practice crop rotation and avoid overcrowding."
    },

    "Peach___healthy": {
        "status": "No disease present",
        "prevention": "Regularly monitor for pests, maintain good soil health."
    },

    "Pepper,_bell___Bacterial_spot": {
        "scientific_name": "Xanthomonas campestris pv. vesicatoria",
        "cause": "Bacterial infection caused by Xanthomonas bacteria.",
        "symptoms": "Water-soaked spots on leaves and fruit, leading to premature drop.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Dilute and spray every 7-14 days.",
                "benefits": "Disrupts bacterial lifecycle and repels pests.",
                "notes": "Best applied in the early morning or late evening."
            },
            "Bacillus subtilis": {
                "application": "Use as a soil drench or foliar spray.",
                "benefits": "Competes with harmful bacteria, reducing their population.",
                "notes": "Can be used preventatively or when symptoms appear."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Follow manufacturer's instructions; typically applied every 7-14 days.",
                "benefits": "Inhibits the growth of bacteria.",
                "notes": "Avoid overuse as it can accumulate in the soil and harm beneficial microbes."
            }
        },
        "familiar_pesticides": ["Copper sulfate", "Streptomycin"],
        "prevention": "Practice crop rotation, avoid overhead watering, and use resistant varieties."
    },

    "Pepper,_bell___healthy": {
        "status": "No disease present",
        "prevention": "Maintain soil health, monitor for pests, and provide adequate drainage."
    },

    "Potato___Early_blight": {
        "scientific_name": "Alternaria solani",
        "cause": "Fungal infection caused by Alternaria solani.",
        "symptoms": "Dark spots on leaves with concentric rings, leading to leaf drop.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Dilute and spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and deters pests.",
                "notes": "Best applied in the early morning or late evening."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow label instructions for application.",
                "benefits": "Controls early blight effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Azoxystrobin"],
        "prevention": "Practice crop rotation and remove infected plant debris."
    },

    "Potato___Late_blight": {
        "scientific_name": "Phytophthora infestans",
        "cause": "Fungal infection caused by Phytophthora infestans.",
        "symptoms": "Water-soaked spots on leaves, stem lesions, and tuber rot.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and deters pests.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a soil drench or foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Controls late blight effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Metalaxyl", "Chlorothalonil"],
        "prevention": "Avoid overcrowding and ensure good air circulation."
    },

    "Potato___healthy": {
        "status": "No disease present",
        "prevention": "Rotate crops and maintain healthy soil."
    },

    "Strawberry___Botrytis_Blight": {
        "scientific_name": "Botrytis cinerea",
        "cause": "Fungal infection caused by Botrytis cinerea.",
        "symptoms": "Gray mold on fruit and foliage.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and deters pests.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Controls Botrytis effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Chlorothalonil", "Fenhexamid"],
        "prevention": "Ensure good air circulation and avoid overhead watering."
    },

    "Strawberry___healthy": {
        "status": "No disease present",
        "prevention": "Maintain good soil health and monitor for pests."
    },

    "Tomato___Bacterial_spot": {
        "scientific_name": "Xanthomonas campestris pv. vesicatoria",
        "cause": "Bacterial infection caused by Xanthomonas bacteria.",
        "symptoms": "Water-soaked spots on leaves and fruit, leading to premature drop.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Dilute and spray every 7-14 days.",
                "benefits": "Disrupts bacterial lifecycle and repels pests.",
                "notes": "Best applied in the early morning or late evening."
            },
            "Bacillus subtilis": {
                "application": "Use as a soil drench or foliar spray.",
                "benefits": "Competes with harmful bacteria, reducing their population.",
                "notes": "Can be used preventatively or when symptoms appear."
            }
        },
        "inorganic_solution": {
            "Copper-based Fungicides": {
                "application": "Follow manufacturer's instructions; typically applied every 7-14 days.",
                "benefits": "Inhibits the growth of bacteria.",
                "notes": "Avoid overuse as it can accumulate in the soil and harm beneficial microbes."
            }
        },
        "familiar_pesticides": ["Copper sulfate", "Streptomycin"],
        "prevention": "Practice crop rotation, avoid overhead watering, and use resistant varieties."
    },

    "Tomato___healthy": {
        "status": "No disease present",
        "prevention": "Maintain soil health, monitor for pests, and provide adequate drainage."
    },

    "Watermelon___Powdery_mildew": {
        "scientific_name": "Podosphaera xanthii",
        "cause": "Fungal infection caused by Podosphaera xanthii.",
        "symptoms": "White powdery spots on leaves and stems.",
        "organic_solution": {
            "Neem Oil": {
                "application": "Spray every 7-14 days.",
                "benefits": "Suppresses fungal growth and repels pests.",
                "notes": "Apply during cooler parts of the day."
            },
            "Bacillus subtilis": {
                "application": "Use as a foliar spray.",
                "benefits": "Competes with harmful fungi.",
                "notes": "Effective preventively or at first sign of symptoms."
            }
        },
        "inorganic_solution": {
            "Fungicide": {
                "application": "Follow manufacturer's instructions.",
                "benefits": "Controls powdery mildew effectively.",
                "notes": "Rotate fungicides to prevent resistance."
            }
        },
        "familiar_pesticides": ["Myclobutanil", "Chlorothalonil"],
        "prevention": "Ensure good air circulation and avoid overhead watering."
    },

    "Watermelon___healthy": {
        "status": "No disease present",
        "prevention": "Maintain healthy plants and monitor for pests."
    }
}


def read_file_as_image(file) -> np.ndarray:
    image = Image.open(BytesIO(file.read()))
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize((256, 256))
    image_array = np.array(image) / 255.0  
    return image_array


@csrf_exempt  
def predict_image(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']  
        try:
            image = read_file_as_image(file)
            img_batch = np.expand_dims(image, axis=0) 
            predictions = MODEL.predict(img_batch)
            predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
            confidence = np.max(predictions[0])*100
            return JsonResponse({
                "filename": file.name,
                "class": predicted_class,
                "confidence": float(confidence)
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method or no file provided."}, status=400)
@login_required
def upload_page(request):
    result = None
    if request.method == 'POST':
        response = predict_image(request)
        if response.status_code == 200:
            result = response.content.decode('utf-8')  
            result = json.loads(result)  
    
    return render(request, 'farmers/upload_and_predict.html', {'result': result})



@login_required
def CommunityView(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False) 
            community.name = request.user  
            community.save() 
            return redirect('community')  
    else:
        form = CommunityForm()  
    communities = Community.objects.all()

    return render(request, "farmers/community.html", {
        'form': form,
        'communities': communities
    })

def remove(request, id):
  
    community = get_object_or_404(Community, id=id) 
    community.delete()  
   
    return redirect("community") 

from .models import FarmerScheme, STATE_CHOICES

def scheme_list(request):
    selected_state = request.GET.get('state')
    schemes = FarmerScheme.objects.all()
    
    if selected_state:
        schemes = schemes.filter(state=selected_state)

    return render(request, 'farmers/scheme_list.html', {
        'schemes': schemes,
        'states': STATE_CHOICES,
        'selected_state': selected_state,
    })

def chat_view(request):
    return render(request,"farmers/chatbot.html")
def weather_view(request):
    return render(request,"farmers/weather.html")
@csrf_exempt
def SolutionView(request):
    disease_name = request.GET.get('disease_name', None)
    if not disease_name:
        return JsonResponse({'error': 'Please provide a disease name'}, status=400)
    disease_info = tomato_disease_data.get(disease_name, None)
    if not disease_info:
        return JsonResponse({'error': 'Disease not found'}, status=404)
    context = {
        'disease_name': disease_name,
        'scientific_name': disease_info['scientific_name'],
        'cause': disease_info['cause'],
        'symptoms': disease_info.get('symptoms', 'No symptoms information available.'),
        'organic_solution': disease_info['organic_solution'],
        'inorganic_solution': disease_info['inorganic_solution'],
        'familiar_pesticides': disease_info['familiar_pesticides'],
        'prevention': disease_info['prevention']
    }
    return render(request, 'farmers/solution.html', context)


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')  
    else:
        form = UserCreationForm()  

    return render(request, 'signup.html', {'form': form})  
        
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on user role
            if user.is_superuser:
                return redirect('admin:index')  # Django admin panel
            elif user.is_staff:
                return redirect('farmer_homepage')
            else:
                next_url = request.GET.get('next')
                return redirect(next_url) if next_url else redirect('vendor_homepage')
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request,"Logout Successfully")
    return redirect('login')


# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>farmer views start here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from django.core.exceptions import ValidationError
from .models import Farmer, Product  
from django.contrib.auth.decorators import login_required  

@login_required
def farmer_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            category = request.POST.get('category')
            price_per_unit = request.POST.get('price_per_unit')
            quantity_available = request.POST.get('quantity_available')
            unit = request.POST.get('unit')
            description = request.POST.get('description')
            image = request.FILES.get('image')  
            if not all([name, category, price_per_unit, quantity_available, unit]):
                raise ValidationError("All required fields must be filled out.")
            try:
                farmer = request.user.farmer  
            except Farmer.DoesNotExist:
                messages.error(request, 'You must have a farmer profile to list products.')
                return redirect('farmer_profile')  
            product = Product(
                farmer=farmer,  
                name=name,
                category=category,
                price_per_unit=price_per_unit,
                quantity_available=quantity_available,
                unit=unit,
                description=description,
            )
            product.save()
            if image:
                product.image = image
                product.save()
            messages.success(request, 'Product listed successfully!')
            return redirect('farmer_homepage')  

        except ValidationError as e:
            messages.error(request, f'Error: {e.message}')
            return render(request, 'farmers/farmer_homepage.html')

    else:
        return render(request, 'farmers/farmer_homepage.html')

    
@login_required
def farmer_productlist_view(request):
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        return redirect('farmer_profile')  
    products = Product.objects.filter(farmer=farmer)
    return render(request, "farmers/product_list.html", {"products": products})   


def add_product(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            category = request.POST.get('category')
            price_per_unit = request.POST.get('price_per_unit')
            quantity_available = request.POST.get('quantity_available')
            unit = request.POST.get('unit')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            
            # Validate required fields
            if not all([name, category, price_per_unit, quantity_available, unit]):
                raise ValidationError("All required fields must be filled out.")
            
            # Get farmer profile
            try:
                farmer = request.user.farmer
            except Farmer.DoesNotExist:
                messages.error(request, 'You must have a farmer profile to list products.')
                return redirect('farmer_profile')
            
            # Create product
            product = Product(
                farmer=farmer,
                name=name,
                category=category,
                price_per_unit=price_per_unit,
                quantity_available=quantity_available,
                unit=unit,
                description=description,
            )
            
            # Save product (twice if image exists)
            product.save()
            if image:
                product.image = image
                product.save()
            
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
            
        except ValidationError as e:
            messages.error(request, f'Error: {e}')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    # GET request or failed POST
    return render(request, 'farmers/add_product.html', {
        'categories': Product.category,
        'units': Product.unit
    })
    
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user.farmer)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            category = request.POST.get('category')
            price_per_unit = request.POST.get('price_per_unit')
            quantity_available = request.POST.get('quantity_available')
            unit = request.POST.get('unit')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            
            # Validate required fields
            if not all([name, category, price_per_unit, quantity_available, unit]):
                raise ValidationError("All required fields must be filled out.")
            
            # Update product
            product.name = name
            product.category = category
            product.price_per_unit = price_per_unit
            product.quantity_available = quantity_available
            product.unit = unit
            product.description = description
            
            if image:
                product.image = image
            
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
            
        except ValidationError as e:
            messages.error(request, f'Error: {e}')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    # GET request or failed POST
    return render(request, 'farmers/edit_product.html', {
        'product': product,
        'categories': Product.category,
        'units': Product.unit
    })
    
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user.farmer)
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
        
        return redirect('product_list')
    
    # GET request (show confirmation)
    return render(request, 'farmers/confirm_delete.html', {'product': product})


@login_required
def farmer_profile_view(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('farmer_homepage')  # Or wherever you want to redirect

    return render(request, 'farmers/profile.html', {'farmer': farmer})


@login_required
def edit_farmer_profile(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('home')  # Redirect wherever appropriate

    if request.method == 'POST':
        farmer.farm_name = request.POST.get('farm_name')
        farmer.contact_number = request.POST.get('contact_number')
        farmer.address = request.POST.get('address')

        if request.FILES.get('profile_image'):
            farmer.profile_image = request.FILES['profile_image']

        farmer.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('farmer_profile')

    return render(request, 'farmers/edit_profile.html', {'farmer': farmer})


    
def farmer_order_view(request):
    return render(request,"farmers/order.html")


# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>farmer views end here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>vendor views start here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def vendor_homepage(request):
    return render(request,"vendors/vendor_homepage.html")


from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Farmer,Cart
from .models import Product, Farmer, PRODUCT_CATEGORY_CHOICES

@login_required
def product_list_view(request):
    products = Product.objects.select_related('farmer').all()

    # Filters
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(price_per_unit__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(price_per_unit__lte=max_price)

    farmer_id = request.GET.get('farmer')
    if farmer_id:
        products = products.filter(farmer_id=farmer_id)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    products = products.order_by('-listed_on')

    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': dict(PRODUCT_CATEGORY_CHOICES),  # ✅ Use the actual choices list here
        'farmers': Farmer.objects.all(),
        'selected_category': category or '',
        'selected_farmer': farmer_id or '',
        'min_price': min_price or '',
        'max_price': max_price or '',
        'search_query': search_query or '',
        'page_obj': page_obj,
    }

    return render(request, 'vendors/products.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            messages.info(request, f"Updated quantity of {product.name}.")
        else:
            messages.success(request, f"Added {product.name} to your cart.")
        return redirect('view_cart')  # or 'product_list', etc.
    return redirect('product_list')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total,
    }
    return render(request, 'vendors/view_cart.html', context)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cart, Product

@csrf_exempt
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity'))

            cart_item = Cart.objects.get(id=item_id, user=request.user)
            product = cart_item.product

            if quantity > product.quantity_available:
                quantity = product.quantity_available

            if quantity < 1:
                quantity = 1

            cart_item.quantity = quantity
            cart_item.save()

            # Recalculate totals
            cart_items = Cart.objects.filter(user=request.user)
            subtotal = sum(item.quantity * item.product.price_per_unit for item in cart_items)
            shipping = 50
            grand_total = subtotal + shipping

            return JsonResponse({
                'success': True,
                'item_total': quantity * product.price_per_unit,
                'subtotal': subtotal,
                'grand_total': grand_total,
                'max_quantity': product.quantity_available,
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = Cart.objects.get(id=item_id, user=request.user)
            cart_item.delete()

            # Recalculate totals
            cart_items = Cart.objects.filter(user=request.user)
            subtotal = sum(item.quantity * item.product.price_per_unit for item in cart_items)
            shipping = 50 if cart_items.exists() else 0
            grand_total = subtotal + shipping

            return JsonResponse({
                'success': True,
                'subtotal': subtotal,
                'grand_total': grand_total,
                'cart_empty': not cart_items.exists()
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


from django.shortcuts import render, redirect
from .models import Vendor
from django.contrib.auth.decorators import login_required

@login_required
def register_vendor_profile(request):
    user = request.user

    if request.method == 'POST':
        vendor_name = request.POST.get('vendor_name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        profile_image = request.FILES.get('profile_image')

        # Save or update vendor
        vendor, created = Vendor.objects.get_or_create(user=user)
        vendor.vendor_name = vendor_name
        vendor.contact_number = contact_number
        vendor.address = address
        vendor.latitude = latitude
        vendor.longitude = longitude
        if profile_image:
            vendor.profile_image = profile_image
        vendor.save()

        return redirect('vendor_homepage')  # Adjust to your actual profile view name

    return render(request, 'vendors/register.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor

@login_required
def vendor_profile_view(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor profile not found.")
        return redirect('vendor_homepage')  # Or your actual vendor home

    return render(request, 'vendors/profile.html', {'vendor': vendor})

@login_required
def edit_vendor_profile(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor profile not found.")
        return redirect('vendor_homepage')  # Adjust redirection

    if request.method == 'POST':
        vendor.vendor_name = request.POST.get('vendor_name')
        vendor.contact_number = request.POST.get('contact_number')
        vendor.address = request.POST.get('address')
        vendor.latitude = request.POST.get('latitude') or None
        vendor.longitude = request.POST.get('longitude') or None

        if request.FILES.get('profile_image'):
            vendor.profile_image = request.FILES['profile_image']

        vendor.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('vendor_profile')

    return render(request, 'vendors/edit_profile.html', {'vendor': vendor})

# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>vendor views end here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib import messages
from io import BytesIO
import os
import razorpay
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .models import Payment
# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>transaction views start here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def ensure_receipt_directory():
    receipt_directory = os.path.join(settings.MEDIA_ROOT, 'receipts')
    if not os.path.exists(receipt_directory):
        os.makedirs(receipt_directory)


@login_required
def create_order(request):
    # Step 1: Get total from URL query parameters (e.g. ?total=500)
    total = request.GET.get("total")
    
    if total:
        try:
            amount = int(float(total) * 100)  # Convert to paise
            email = request.user.email

            # Step 2: Create order in Razorpay
            razorpay_order = razorpay_client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })

            # Step 3: Save order in database
            order = Payment.objects.create(
                user=request.user,
                order_id=razorpay_order["id"],
                amount=amount / 100,  # Store in INR
                email=email,
                status="Created"
            )

            # Step 4: Render checkout page with order details
            context = {
                "order": order,
                "razorpay_key": settings.RAZORPAY_KEY_ID
            }
            return render(request, "transaction/checkout.html", context)

        except Exception as e:
            messages.error(request, f"Error while creating payment order: {e}")
            return redirect("view_cart")  # Fallback to cart

    # Fallback if total is missing
    messages.error(request, "Invalid total amount.")
    return redirect("view_cart")

from .models import Payment, Cart, Order, OrderItem


@csrf_exempt
@login_required
def payment_success(request):
    if request.method == "POST":
        order_id = request.POST.get("razorpay_order_id")
        payment_id = request.POST.get("razorpay_payment_id")
        signature = request.POST.get("razorpay_signature")

        params_dict = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            status = "Completed"
        except:
            status = "Failed"

        payment = Payment.objects.filter(order_id=order_id).first()
        if payment:
            payment.payment_id = payment_id
            payment.status = status
            payment.save()

            # Only create order if payment was successful
            if status == "Completed":
                if not hasattr(payment, 'order'):
                    cart_items = Cart.objects.filter(user=request.user)
                    total_amount = sum(item.total_price for item in cart_items)

                    order = Order.objects.create(
                        user=request.user,
                        payment=payment,
                        total_amount=total_amount
                    )

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price_per_unit
                        )
                        item.product.quantity_available -= item.quantity
                        item.product.save()

                    cart_items.delete()

                    # Generate and attach receipt
                    ensure_receipt_directory()
                    receipt_pdf = generate_receipt(payment)
                    payment.receipt_pdf = receipt_pdf
                    payment.save()

                    # Send receipt email
                    send_receipt_email(payment)

                    return render(request, "transaction/payment_success.html", {"order": order})
                
                # If order already exists
                return render(request, "transaction/payment_success.html", {"order": payment.order})

        return render(request, "transaction/payment_failed.html", {"error": "Payment record not found."})

    return redirect("view_cart")


def generate_receipt(payment):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 40, "Infinite Igniters")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 60, " Address:dehradun | Contact Number:7453966532 | Email:joshiharish942@gmail.com")

   
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, height - 100, "Payment Receipt")

   
    p.setStrokeColor(colors.black)
    p.line(100, height - 110, width - 100, height - 110)

    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 140, "Payment Details")
    
    
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 160, f"Order ID: {payment.order_id}")
    p.drawString(100, height - 180, f"Payment ID: {payment.payment_id}")
    p.drawString(100, height - 200, f"Amount: ₹{payment.amount}")
    p.drawString(100, height - 220, f"Status: {payment.status}")
    
    
    email = payment.email if payment.email else "Email not provided"
    p.drawString(100, height - 240, f"Email: {email}")

   
    p.drawString(100, height - 260, f"Username: {payment.user.username}")
    p.drawString(100, height - 280, f"User ID: {payment.user.id}")
    
    
    p.line(100, height - 290, width - 100, height - 290)

    
    p.setFont("Helvetica", 10)
    p.drawString(100, 40, "Thank you for your payment!")
    p.drawString(100, 20, "For inquiries, contact Infinite Igniters at: contact@infinite.com")

    
    file_name = f"receipt_{payment.order_id}.pdf"
    receipt_directory = os.path.join(settings.MEDIA_ROOT, 'receipts')

    
    if not os.path.exists(receipt_directory):
        os.makedirs(receipt_directory)

    file_path = os.path.join(receipt_directory, file_name)
    
    
    p.save()

    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())

    return file_path


def send_receipt_email(payment):
    
    email = EmailMessage(
        subject="Your Payment Receipt",
        body=f"Dear {payment.user.username},\n\nThank you for your payment. Find your receipt attached.\n\nOrder ID: {payment.order_id}\nAmount: ₹{payment.amount}",
        from_email=settings.EMAIL_HOST_USER,
        to=[payment.user.email],
    )

    
    with open(payment.receipt_pdf.path, "rb") as f:
        email.attach(f"receipt_{payment.order_id}.pdf", f.read(), "application/pdf")

    email.send()





# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>transaction views end here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>from .models import Order

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'vendors/order.html', {'orders': orders})


from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required
def staff_orders_view(request):
    user = request.user  # must be staff (checked by decorator)

    # Make sure the user is a Farmer instance and not just a User instance
    try:
        farmer = Farmer.objects.get(user=user)
    except Farmer.DoesNotExist:
        # Handle the case where the user is not a farmer
        farmer = None

    if farmer:
        # Filter order items where the product belongs to this farmer
        order_items = OrderItem.objects.filter(product__farmer=farmer).select_related('order', 'product')

        # Group order items by order
        orders = {}
        for item in order_items:
            if item.order.id not in orders:
                orders[item.order.id] = {
                    "order": item.order,
                    "items": []
                }
            orders[item.order.id]["items"].append(item)

        return render(request, "farmers/order.html", {"orders": orders})
    else:
        # Handle the case when the user is not a farmer
        return render(request, "farmers/order.html", {"orders": []})


import os
import json
import re
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Set Groq API key
os.environ["GROQ_API_KEY"] = "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"  # replace this with a real key

llm = ChatGroq(
    temperature=0.3,
    model_name="llama3-70b-8192"
)

# Generate plant-related questions
def get_plant_questions():
    prompt_text = """
    You're a plant care expert. Ask up to 5 smart and relevant questions that would help you understand a user's plant and provide care advice. Return JSON like:

    {
      "questions": [
        "What is the plant name?",
        "Is it kept indoors or outdoors?",
        "What kind of climate is it in?",
        "Are there any visible problems?",
        "How often is it watered?"
      ]
    }
    """
    result = llm.invoke(prompt_text)
    return result.content.strip()

# Generate plant care advice based on user answers
def get_plant_solution(answers_dict):
    prompt = ChatPromptTemplate.from_template("""
    Based on the user's answers about their plant, provide helpful plant care advice in this JSON format:

    {{
      "plant": "<Plant Name>",
      "summary": "<Brief summary of the user's situation>",
      "care_advice": "<Detailed care guidance>",
      "tips": [
        "<Tip 1>",
        "<Tip 2>",
        "... up to 5"
      ]
    }}

    User's answers:
    {answers}
    """)
    chain = prompt | llm
    result = chain.invoke({"answers": json.dumps(answers_dict)})
    return result.content.strip()

# View to show plant questions
def ask_plant_questions(request):
    if request.method == "GET":
        raw = get_plant_questions()
        try:
            match = re.search(r"(\{.*?\})", raw, re.DOTALL)
            if match:
                questions_json = json.loads(match.group(1))
                return render(request, "farmers/plant_questions.html", {"questions": questions_json["questions"]})
        except Exception as e:
            return render(request, "farmers/plant_questions.html", {"error": "Failed to generate questions."})
    return render(request, "farmers/plant_questions.html")

# View to receive answers and show solution
@csrf_exempt
def plant_solution(request):
    if request.method == "POST":
        try:
            answers_dict = {key: value for key, value in request.POST.items()}
            raw = get_plant_solution(answers_dict)

            match = re.search(r"(\{.*?\})", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                return render(request, "farmers/plant_solution.html", {"result": data})
            else:
                raise ValueError("Invalid JSON format in response.")
        except Exception as e:
            return render(request, "farmers/plant_solution.html", {"error": f"Failed to generate solution: {str(e)}"})
    return render(request, "farmers/plant_solution.html")
