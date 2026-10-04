from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib.auth.decorators import login_required




def first_page(request):
    return render(request, 'first_page.html')

def partner_page(request):
    return render(request, 'partner_page.html')





from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from .forms import *
from django.core.cache import cache
import random
from django.core.validators import validate_email
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

def registration(request):
    if request.method == 'POST':
        data = request.POST
        fname = data.get('fname', '').strip()
        lname = data.get('lname', '').strip()
        username = data.get('username', '').strip().lower()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        required_fields = {
            'First Name': fname,
            'Last Name': lname,
            'Username': username,
            'Email': email,
            'Password': password,
            'Confirm Password': confirm_password
        }

        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "register.html")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format!")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "register.html")

        try:
            # Create active user directly (NO EMAIL VERIFICATION)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=fname,
                last_name=lname,
                is_active=True  # Active immediately
            )

            messages.success(request, "Registration successful! You can now login.")
            return redirect('user_login')

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "register.html")

    return render(request, "register.html")

def reset_password(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, 'Session expired. Please start the process again.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                try:
                    user = User.objects.get(email=email)
                    
                    # Debug output
                    print(f"Resetting password for user: {user.username} (email: {email})")
                    
                    # Explicitly set and save password
                    user.set_password(new_password)
                    user.save()
                    
                    # Clear the session
                    del request.session['email']
                    if 'otp' in request.session:
                        del request.session['otp']
                    
                    messages.success(request, 'Password reset successfully! Please log in with your new password.')
                    
                    # Check your URL name - it needs to match exactly what's in your urls.py
                    # If your URL pattern is named 'login' and not 'user_login', change this line
                    return redirect('user_login')  # Make sure this matches your URL name
                    
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
            else:
                messages.error(request, 'Passwords do not match.')
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form})

# Now let's fix the user_login function with more robust debugging
# First, make sure you have all these imports at the top of your file
from django.contrib.auth import authenticate, login
from django.core.cache import cache

def user_login(request):
    if request.method == 'POST':
        ip_address = request.META.get('REMOTE_ADDR', '')
        attempt_count = cache.get(f'login_attempts_{ip_address}', 0)

        if attempt_count >= 3:
            messages.error(request, "Too many attempts. Try again in 15 minutes.")
            return render(request, 'login.html')

        username_or_email = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '')
        
        # More detailed debugging
        print(f"Login attempt for: {username_or_email}")
        print(f"Password length: {len(password)}")
        
        # Try to fetch user first to verify existence
        user_obj = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username_to_use = user_obj.username
                print(f"Found user by email: {username_to_use}")
            except User.DoesNotExist:
                username_to_use = username_or_email
                print("No user found with this email")
        else:
            try:
                user_obj = User.objects.get(username=username_or_email)
                username_to_use = username_or_email
                print(f"Found user by username: {username_to_use}")
            except User.DoesNotExist:
                username_to_use = username_or_email
                print("No user found with this username")
        
        # Now try to authenticate
        user = authenticate(username=username_to_use, password=password)
        print(f"Authentication result: {'Success' if user else 'Failed'}")

        if user is not None:
            if user.is_active:
                login(request, user)
                cache.delete(f'login_attempts_{ip_address}')
                return redirect('index')
            else:
                messages.error(request, "Account not activated.")
        else:
            cache.set(f'login_attempts_{ip_address}', attempt_count + 1, 900)
            messages.error(request, "Invalid credentials. Please check your username/email and password.")

        return render(request, 'login.html')

    return render(request, 'login.html')


import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import EmailForm, OTPForm, ResetPasswordForm
import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
# Modify your forgot_password function to store OTP in session
def forgot_password(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = str(random.randint(100000, 999999))
                
                # Store OTP in session instead of otp_store
                request.session['email'] = email
                request.session['otp'] = otp  # Store OTP in session

                send_mail(
                    'Your OTP Code',
                    f'Your OTP for password reset is {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return redirect('verify_otp')
            except User.DoesNotExist:
                messages.error(request, 'No user found with that email.')
    else:
        form = EmailForm()
    return render(request, 'forgot_password.html', {'form': form})

# Modified verify_otp function with proper debugging
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        correct_otp = request.session.get('otp')
        
        # Add debugging to see what's happening
        print(f"User entered OTP: {user_otp}")
        print(f"Correct OTP from session: {correct_otp}")

        if user_otp == correct_otp:
            # OTP is correct - clear the OTP but keep the email
            del request.session['otp']  # Remove OTP after successful verification
            return redirect('reset_password')  # Redirect to password reset page
        else:
            # OTP is incorrect
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'verify_otp.html')

def reset_password(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, 'Session expired. Please start the process again.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                try:
                    user = User.objects.get(email=email)
                    # Use set_password properly and save
                    user.set_password(new_password)
                    user.save()
                    
                    # Clear session data
                    del request.session['email']
                    if 'otp' in request.session:
                        del request.session['otp']
                    
                    messages.success(request, 'Password reset successfully! Please log in with your new password.')
                    return redirect('user_login')
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
            else:
                messages.error(request, 'Passwords do not match.')
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form})





def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('user_login')





@login_required
def index(request, women_category=None, men_category=None):
    if women_category:
        products = Product.objects.filter(type=women_category, category='Women')
    else:
        products = Product.objects.filter(category='Women')

    if men_category:
        products1 = Product.objects.filter(type=men_category, category='Men')
    else:
        products1 = Product.objects.filter(category='Men')

    return render(request, 'index.html', {
        'products': products, 
        'products1': products1, 
        'selected_women_category': women_category, 
        'selected_men_category': men_category
    })


@login_required
def men_clothes(request):
    products = Product.objects.filter(category='Men')

    # Get filter values from the request
    type_ = request.GET.get('type')  # 'type' is a reserved keyword, so use 'type_' 
    subtype = request.GET.get('subtype')
    size = request.GET.get('size')
    color = request.GET.get('color')

    # Apply additional filters only to Men's clothing
    if type_:
        products = products.filter(type=type_)
    if subtype:
        products = products.filter(subtype=subtype)
    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color=color)
    return render(request, 'men_clothes.html',{'products': products})


@login_required
def women_clothes(request):
    products = Product.objects.filter(category='Women')
    type_ = request.GET.get('type')  # 'type' is a reserved keyword, so use 'type_' 
    subtype = request.GET.get('subtype')
    size = request.GET.get('size')
    color = request.GET.get('color')

    # Apply additional filters only to Men's clothing
    if type_:
        products = products.filter(type=type_)
    if subtype:
        products = products.filter(subtype=subtype)
    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color=color)
    return render(request, 'women_clothes.html', {'products': products})


@login_required
def shop(request):
    category = request.GET.get('category')
    type_ = request.GET.get('type')  # 'type' is a reserved keyword, so use 'type_' 
    subtype = request.GET.get('subtype')
    size = request.GET.get('size')
    color = request.GET.get('color')

    # Start with all products
    products = Product.objects.all()

    # Apply filters based on selected options
    if category:
        products = products.filter(category=category)
    if type_:
        products = products.filter(type=type_)
    if subtype:
        products = products.filter(subtype=subtype)
    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color=color)
    return render(request, 'shop.html',{'products': products})


    return render(request, 'shop.html')

    
def AI_design(request):
    return render(request,'AI-design.html')


@login_required
def contact(request):
    return render(request, 'contact.html')


@login_required
def check_out(request):
   
    return render(request, 'check-out.html')


@login_required
def recommendation(request):
   
    return render(request, 'recommendation.html')


@login_required
def product_detail(request, product_name):
    # Retrieve all comments for the product, ordered by creation date
    comments = Comments.objects.all().order_by('-created_at')
    
    # Handle form submission (POST request)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        rating = request.POST.get('rating')
        message = request.POST.get('message')
        
        # Check if all fields are filled
        if name and email and message and rating: 
            # Create a new comment
            Comments.objects.create(
                name=name, email=email, rating=rating, message=message
            )
            messages.success(request, 'Your comment has been submitted successfully!')
            comments = Comments.objects.all().order_by('-created_at')  # Refresh comments
        else:
            messages.error(request, 'Please fill in all fields before submitting.')

    # Fetch the product based on the provided product_id
    product = get_object_or_404(Product, name=product_name)
    products = Product.objects.all()  # Fetch all products (if needed elsewhere in the page)
    
    # Combine all data into a single context dictionary
    context = {
        'product': product,   # Pass the selected product
        'products': products, # Pass all products (if needed)
        'comments': comments, # Pass the comments for the product
    }

    # Render the template with the context
    return render(request, 'product.html', context)



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages


@login_required
def cart(request, product_id):
    """
    Adds a product to the cart and updates session data.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', 1))  # Get quantity from POST, default to 1
        except ValueError:
            quantity = 1  # If invalid quantity, default to 1

        cart = request.session.get('cart', {})  # Retrieve cart from session

        # Update the product quantity if it already exists in the cart
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += quantity
        else:
            # Add new product to the cart
            cart[str(product_id)] = {
                'name': product.name,
                'price': float(product.price),  # Convert Decimal to float
                'quantity': quantity,
                'image': product.hero_image.url if product.hero_image else None,
            }

        request.session['cart'] = cart  # Save updated cart back to session
        messages.success(request, f"{product.name} added to the cart successfully!")
        return redirect('shopping_cart')  # Redirect to the shopping cart page

    return redirect('shop')  # Redirect to shop page if accessed without POST


@login_required
def shopping_cart(request):
    """
    Renders the shopping cart page with cart items and calculates totals.
    """
    cart = request.session.get('cart', {})
    subtotal = 0
    cart_items_count = 0
    mini_cart = []

    # Calculate subtotal, total items, and build mini-cart data
    for key, item in cart.items():
        item_total = float(item['price']) * int(item['quantity'])
        subtotal += item_total
        cart_items_count += int(item['quantity'])
        mini_cart.append({
            'name': item['name'],
            'quantity': item['quantity'],
            'price': float(item['price']),
            'image': item['image'],
            'total_price': round(item_total, 2),
        })

    # Pass data to the template
    context = {
        'cart': cart,
        'subtotal': round(subtotal, 2),  # Total before additional fees
        'total': round(subtotal, 2),    # Modify for tax or shipping if needed
        'cart_items_count': cart_items_count,
        'mini_cart': mini_cart,
    }
    return render(request, 'shopping-cart.html', context)



@login_required
def remove_from_cart(request, product_id):
    """
    Removes a product from the cart and updates session data.
    """
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]  # Remove the item from the cart
        request.session['cart'] = cart
        messages.success(request, "Item removed from the cart!")
    return redirect('shopping_cart')







@login_required
def filter_dresses_women(request):
    if request.method == "POST":
        # Get form inputs
        face_color = request.POST.get('face_color', '').lower()
        hair_color = request.POST.get('hair_color', '').lower()
        skin_type = request.POST.get('skin_type', '').lower()
        dress_type = request.POST.get('dress_type', '').lower()

        # Initialize query for WOMEN'S products
        dresses = Product.objects.filter(category='Women')  # Base query

        # Define filtering logic (CHAIN FROM dresses QUERYSET)
        if face_color == "fair":
            if hair_color == "black":
                if skin_type == "oily" and dress_type == "party":
                    dresses = dresses.filter(type="Party Wear", color="Dark")  # Chain here
                elif skin_type == "dry" and dress_type == "casual":
                    dresses = dresses.filter(type="Casual Wear", color="Light")
                elif skin_type == "combination" and dress_type == "formal":
                    dresses = dresses.filter(type="Formal Wear", color="Dark")
            elif hair_color == "brown" and dress_type == "seasonal":
                dresses = dresses.filter(type="Seasonal Wear", color="Light")

        elif face_color == "medium":
            if hair_color == "brown":
                if skin_type == "oily" and dress_type == "party":
                    dresses = dresses.filter(type="Party Wear", color="Light")
                elif skin_type == "dry" and dress_type == "casual":
                    dresses = dresses.filter(type="Casual Wear", color="Dark")
                elif skin_type == "combination" and dress_type == "formal":
                    dresses = dresses.filter(type="Formal Wear", color="Light")
            elif hair_color == "black" and dress_type == "seasonal":
                dresses = dresses.filter(type="Seasonal Wear", color="Dark")

        elif face_color == "dark":
            if hair_color == "black":
                if skin_type == "oily" and dress_type == "party":
                    dresses = dresses.filter(type="Party Wear", color="Light")
                elif skin_type == "dry" and dress_type == "casual":
                    dresses = dresses.filter(type="Casual Wear", color="Dark")
                elif skin_type == "combination" and dress_type == "formal":
                    dresses = dresses.filter(type="Formal Wear", color="Dark")
            elif hair_color == "brown" and dress_type == "seasonal":
                dresses = dresses.filter(type="Seasonal Wear", color="Light")

        # Handle cases with no matching dresses
        if not dresses.exists():
            messages.info(request, "No dresses found matching your criteria.")
        return render(request, "filtered_dresses.html", {"dresses": dresses})

    return render(request, "filter_form.html")


@login_required
def filter_dresses_men(request):
    if request.method == "POST":
        # Get form inputs
        face_color = request.POST.get('face_color', '').lower()
        hair_color = request.POST.get('hair_color', '').lower()
        skin_type = request.POST.get('skin_type', '').lower()
        dress_type = request.POST.get('dress_type', '').lower()

        # Initialize query for men's products
        products = Product.objects.filter(category='Men')
        
        # Define men-specific filtering logic
        if face_color == "fair":
            if hair_color == "black":
                if skin_type == "oily" and dress_type == "party":
                    products = products.filter(type="Party Wear", color="Dark", subtype__in=['Shirts', 'Blazers'])
                elif skin_type == "dry" and dress_type == "casual":
                    products = products.filter(type="Casual Wear", color="Light", subtype__in=['T-Shirts', 'Polo Shirts'])
                elif skin_type == "combination" and dress_type == "formal":
                    products = products.filter(type="Formal Wear", color="Dark", subtype__in=['Dress Shirts', 'Suits'])

            elif hair_color == "brown" and dress_type == "seasonal":
                products = products.filter(type="Seasonal Wear", color="Light", subtype__in=['Light Jackets', 'Chinos'])

        elif face_color == "medium":
            if hair_color == "brown":
                if skin_type == "oily" and dress_type == "party":
                    products = products.filter(type="Party Wear", color="Light", subtype__in=['Printed Shirts', 'Designer Jeans'])
                elif skin_type == "dry" and dress_type == "casual":
                    products = products.filter(type="Casual Wear", color="Dark", subtype__in=['Hoodies', 'Joggers'])
                elif skin_type == "combination" and dress_type == "formal":
                    products = products.filter(type="Formal Wear", color="Light", subtype__in=['Tailored Shirts', 'Dress Pants'])

            elif hair_color == "black" and dress_type == "seasonal":
                products = products.filter(type="Seasonal Wear", color="Dark", subtype__in=['Leather Jackets', 'Bootcut Jeans'])

        elif face_color == "dark":
            if hair_color == "black":
                if skin_type == "oily" and dress_type == "party":
                    products = products.filter(type="Party Wear", color="Light", subtype__in=['Silk Shirts', 'Designer Trousers'])
                elif skin_type == "dry" and dress_type == "casual":
                    products = products.filter(type="Casual Wear", color="Dark", subtype__in=['Denim Shirts', 'Cargo Pants'])
                elif skin_type == "combination" and dress_type == "formal":
                    products = products.filter(type="Formal Wear", color="Dark", subtype__in=['Three-piece Suits', 'Oxford Shirts'])

            elif hair_color == "brown" and dress_type == "seasonal":
                products = products.filter(type="Seasonal Wear", color="Light", subtype__in=['Trench Coats', 'Wool Trousers'])

        # Handle no matches
        if not products.exists():
            messages.info(request, "No matching outfits found for your selection.")
            products = Product.objects.none()

        return render(request, "filtered_dresses.html", {
            "dresses": products,  # Key changed from "products" to "dresses"
            "selections": {  # Optional: Only include if used in the template
                "face_color": face_color,
                "hair_color": hair_color,
                "skin_type": skin_type,
                "dress_type": dress_type
            }
        })

    return render(request, "filter_form_men.html")



# @login_required
# def search_products(request):
#     query = request.GET.get('q')  # Retrieve the search query from the input field
#     results = Product.objects.all()  # Start with all products
    
#     # Apply search filter if query is provided
#     if query:
#         results = results.filter(name__icontains=query)

#     # Retrieve additional filter parameters
#     category = request.GET.get('category')
#     type_ = request.GET.get('type')  # Ensure the model field is correctly named
#     subtype = request.GET.get('subtype')
#     size = request.GET.get('size')
#     color = request.GET.get('color')

#     # Apply filters to the search results
#     if category:
#         results = results.filter(category=category)
#     if type_:
#         results = results.filter(type=type_)  # Ensure 'type' exists in the model
#     if subtype:
#         results = results.filter(subtype=subtype)
#     if size:
#         results = results.filter(size=size)
#     if color:
#         results = results.filter(color=color)
#     return render(request, 'search_results.html', {'products': results})
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

@login_required
def search_products(request):
    query = request.GET.get('q', '')
    results = Product.objects.all()
    
    # Process search query for intelligent filtering
    if query:
        # Normalize and split query into terms
        query_terms = query.lower().split()
        category_matches = []
        type_matches = []
        subtype_matches = []
        free_text_terms = []

        # Helper function to find matches in model choices
        def find_matches(term, choices):
            return [value for value, _ in choices 
                   if term in value.lower().replace('-', ' ')]

        for term in query_terms:
            # Check category matches
            category_results = find_matches(term, Product.CATEGORY_CHOICES)
            if category_results:
                category_matches.extend(category_results)
                continue
                
            # Check type matches
            type_results = find_matches(term, Product.TYPE_CHOICES)
            if type_results:
                type_matches.extend(type_results)
                continue
                
            # Check subtype matches
            subtype_results = find_matches(term, Product.SUBTYPE_CHOICES)
            if subtype_results:
                subtype_matches.extend(subtype_results)
                continue
                
            # Add to free text search terms
            free_text_terms.append(term)

        # Apply category filters
        if category_matches:
            results = results.filter(category__in=category_matches)
            
        # Apply type filters
        if type_matches:
            results = results.filter(type__in=type_matches)
            
        # Apply subtype filters
        if subtype_matches:
            results = results.filter(subtype__in=subtype_matches)
            
        # Apply free text search across multiple fields
        if free_text_terms:
            query_filter = Q()
            for term in free_text_terms:
                query_filter &= (
                    Q(name__icontains=term) |
                    Q(description__icontains=term) |
                    Q(features__icontains=term) |
                    Q(introduction__icontains=term)
                )
            results = results.filter(query_filter)

    # Handle additional filter parameters
    filter_params = {
        'category': request.GET.get('category'),
        'type': request.GET.get('type'),
        'subtype': request.GET.get('subtype'),
        'size': request.GET.get('size'),
        'color': request.GET.get('color')
    }

    # Apply additional filters
    for field, value in filter_params.items():
        if value:
            results = results.filter(**{field: value})

    # Pagination and template rendering
    paginator = Paginator(results, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'current_filters': {
            'q': query,
            **filter_params
        },
        'filter_choices': {
            'categories': Product.CATEGORY_CHOICES,
            'types': Product.TYPE_CHOICES,
            'subtypes': Product.SUBTYPE_CHOICES,
            'sizes': Product.SIZE,
            'colors': Product.COLOR_CHOICES
        }
    }
    
    return render(request, 'search_results.html', context)




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from decimal import Decimal

@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')  # Redirect to cart if it's empty

    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    # Create the order
    order = Order.objects.create(user=request.user, total_price=total)

    # Add order items
    for key, item in cart.items():
        OrderItem.objects.create(
            order=order,
            product_name=item['name'],
            price=Decimal(item['price']),
            quantity=item['quantity'],
            image=item['image']
        )

    # Clear the cart
    request.session['cart'] = {}

    return redirect('order_confirmation', order_id=order.id)



from django.utils.timezone import now, timedelta

@login_required
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user, is_cancelled=False)
    except Order.DoesNotExist:
        return redirect('orders')  # Redirect if the order doesn't exist or is already cancelled

    # Check if the order is within the cancellation window (24 hours)
    if now() - order.created_at > timedelta(hours=24):
        return render(request, 'order_error.html', {'message': 'You can only cancel orders within 24 hours.'})

    order.is_cancelled = True
    order.save()
    return redirect('orders')



@login_required
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return redirect('orders')

    return render(request, 'order_confirmation.html', {'order': order})







from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomDesign


@login_required
def tshirt_designer(request):
    
    return render(request, 'AI-design.html')





# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot_logic import get_chatbot_response
import json  # Add this import

@csrf_exempt
def chatbot_view(request):
    if request.method == 'GET':
        return render(request, 'chat.html')
    
    elif request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            user_input = data.get('message', '').strip()
            
            if not user_input:
                return JsonResponse({'error': 'Empty input'}, status=400)
            
            response = get_chatbot_response(user_input)
            return JsonResponse({'response': response})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)




from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .recommendation_chatbot import get_chatbot_response_recomm
import json  # Add this import

@csrf_exempt
def chatbot_view_recomm(request):
    if request.method == 'GET':
        return render(request, 'recommendation_chatbot.html')
    
    elif request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            user_input = data.get('message', '').strip()
            
            if not user_input:
                return JsonResponse({'error': 'Empty input'}, status=400)
            
            response = get_chatbot_response_recomm(user_input)
            return JsonResponse({'response': response})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)




from django.shortcuts import render
from .models import Product

def product_list(request):
    # Get filter parameters from request
    category = request.GET.get('category')
    type_ = request.GET.get('type')  # 'type' is a reserved keyword, so use 'type_' 
    subtype = request.GET.get('subtype')
    size = request.GET.get('size')
    color = request.GET.get('color')

    # Start with all products
    products = Product.objects.all()

    # Apply filters based on selected options
    if category:
        products = products.filter(category=category)
    if type_:
        products = products.filter(type=type_)
    if subtype:
        products = products.filter(subtype=subtype)
    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color=color)

    return render(request, 'sidebar.html', {'products': products})







from django.shortcuts import render, redirect
from .forms import BrandSubmissionForm

def submit_brand(request):
    if request.method == 'POST':
        form = BrandSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'thank_you.html')
    else:
        form = BrandSubmissionForm()
    return render(request, 'submit_brand.html', {'form': form})



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .Serializer import FileUploadSerializer

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
