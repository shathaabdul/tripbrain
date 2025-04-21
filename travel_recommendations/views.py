from django.shortcuts import render, redirect
from .forms import TravelPreferenceForm
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from openai import OpenAI
from datetime import datetime
from .utils import get_city_images 

import json

import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# GPT client setup

# Page 1: Form
def home(request):
    if request.method == 'POST':
        form = TravelPreferenceForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            # Convert dates and calculate trip duration
            start_date = cleaned_data['start_date']
            end_date = cleaned_data['end_date']
            cleaned_data['start_date'] = start_date.strftime('%Y-%m-%d')
            cleaned_data['end_date'] = end_date.strftime('%Y-%m-%d')
            cleaned_data['trip_days'] = (end_date - start_date).days + 1

            request.session['preferences'] = cleaned_data
            return redirect('city_results')
    else:
        form = TravelPreferenceForm()

    return render(request, 'travel_recommendations/home.html', {'form': form})


# Page 2: GPT-based city recommendations
def city_results(request):
    preferences = request.session.get('preferences')
    if not preferences:
        return redirect('home')

    prompt = f"""
    You are a helpful travel assistant.

    The user is planning a {preferences['trip_days']}-day trip from {preferences['start_date']} to {preferences['end_date']}.
    They are in the {preferences['age_range']} age range, traveling with {preferences['companions']}, and prefer a {preferences['city_type']} type of city.
    Their total budget is {preferences['budget']}, and they would like to visit a destination within the continent of {preferences['continent']}.

    Your task:
    - Recommend exactly 5 real-world cities located in {preferences['continent']}.
    - Each city must align with the user’s budget, trip duration, and travel preferences.
    - Choose popular but appropriate destinations for someone with this budget and group type.

    Return only a clean Python list with 5 city names like:
    ["Tbilisi", "Amman", "Cairo"]
    """



    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    reply = response.choices[0].message.content.strip()

    try:
        cities = json.loads(reply)
    except:
        cities = ["Jeddah", "Abu Dhabi", "Doha"]

    return render(request, 'travel_recommendations/city_results.html', {
        'cities': cities
    })

def city_plan(request, city_name): 
    preferences = request.session.get('preferences')
    if not preferences:
        return redirect('home')

    prompt = f"""
You are a smart travel assistant helping a user plan a trip.

Details:
- Trip location: {city_name}
- Duration: {preferences['trip_days']} days (from {preferences['start_date']} to {preferences['end_date']})
- Age range: {preferences['age_range']}
- Travel companions: {preferences['companions']}
- Preferred city type: {preferences['city_type']}
- Budget: {preferences['budget']}
- Continent: {preferences['continent']}

Please create a detailed travel itinerary for {city_name} based on these preferences.

Your plan should include:
1. 5 suitable hotel areas based on the budget and city type
2. A full daily plan for each day (activities, times, locations)
3. 5 recommended restaurants — 
4. 5 recommended cafés — include the name 
5. 5 unique local experiences — include the name 
6. 3 recommended telecom companies for internet SIM/data (local to the country)

⚠️ Format clearly and return real, **clickable Google Maps links** next to each restaurant, café, and experience — like:


The response should be clean and organized for readability.
"""



    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    plan = response.choices[0].message.content.strip()

    # 🔥 Get image URL for the city using Pexels API
    images = get_city_images(city_name, count=3)  # Get 4 photos

    return render(request, 'travel_recommendations/city_plan.html', {
        'city': city_name,
        'plan': plan,
        # 'image_urls': images
    })


# # Page 3: GPT-generated plan
# def city_plan(request, city_name): 
#     preferences = request.session.get('preferences')
#     if not preferences:
#         return redirect('home')

#     # prompt = ... ← skip for now

#     # response = client.chat.completions.create(...)
#     # plan = response.choices[0].message.content.strip()
#     plan = "Test Plan: Welcome to your trip page for " + city_name  # 🔹 temporary placeholder

#     # Optional: comment out image fetching too
#     # images = get_city_images(city_name, count=3)

#     return render(request, 'travel_recommendations/city_plan.html', {
#         'city': city_name,
#         'plan': plan,
#         # 'image_urls': images
#     })


# PDF Download View
def download_plan_pdf(request, city_name):
    preferences = request.session.get('preferences')
    if not preferences:
        return redirect('home')

    prompt = f"""
    You are a helpful travel assistant.

    The user is planning a {preferences['trip_days']}-day trip to {city_name}, 
    from {preferences['start_date']} to {preferences['end_date']}.
    They are in the {preferences['age_range']} age range, 
    traveling with {preferences['companions']},
    and prefer a {preferences['city_type']} type of city.
    Their total budget is {preferences['budget']}, 
    and the city is in the continent of {preferences['continent']}.

    Please provide a structured travel itinerary with the following sections:
    1. Hotel Areas – Recommend 5 suitable areas to stay in the city with brief descriptions
    2. Daily Plan – Activities for each day (clearly labeled Day 1, Day 2, etc.)
    3. Top 5 Restaurants – Include the name 
    4. Top 5 Cafés – Include the name 
    5. 5 Unique Local Experiences – Include the name 
    6. 3 Telecom Companies – For mobile internet and SIM cards

    Be clear, organized, and include line breaks between sections.
    """


    # and a real Google Maps URL (e.g. Central Cafe – https://g.co/kgs/abc123)
    # and a real Google Maps URL
    # and a real Google Maps URL


    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    plan = response.choices[0].message.content.strip()

    template_path = 'travel_recommendations/plan_pdf.html'
    context = {
        'city': city_name,
        'plan': plan,
        'preferences': preferences
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{city_name}_travel_plan.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation failed')

    return response