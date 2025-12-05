from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.http import JsonResponse
from django.utils import timezone
import datetime
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm, ProductForm
from .models import Product, Cart, CartItem, Profile

User = get_user_model()

# ===== РОЛИ =====
def apply_role(user):
    if not hasattr(user, "profile"):
        Profile.objects.create(user=user)

    # Local admin by email
    if user.email == "talgatulyakarys2008@gmail.com":
        user.profile.role = "admin"
        user.profile.save()

    # Keycloak admin
    if user.username == "dev-user":
        user.profile.role = "admin"
        user.profile.save()

    return user.profile.role


# ===== ГЛАВНАЯ =====
def index(request):
    products = Product.objects.all()
    
    # Поиск по названию
    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(name__icontains=search)
    
    # Фильтр по цене
    price_filter = request.GET.get('price_filter', '')
    if price_filter == 'cheap':
        products = products.order_by('price')
    elif price_filter == 'expensive':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')
    
    return render(request, "shop/index.html", {
        "products": products,
        "search": search,
        "price_filter": price_filter
    })


# ===== РЕГИСТРАЦИЯ =====
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            apply_role(user)
            login(request, user)
            messages.success(request, _("Регистрация успешна. Вы вошли."))
            return redirect("shop:index")
    else:
        form = RegisterForm()
    return render(request, "shop/register.html", {"form": form})


# ===== ЛОГИН =====
from django.contrib.auth import logout as django_logout

def login_view(request):

    if request.GET.get("force"):
        django_logout(request)

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"]
            password = form.cleaned_data["password"]
            user = None

            # email логин
            if "@" in identifier:
                try:
                    u = User.objects.get(email__iexact=identifier)
                    user = authenticate(request, username=u.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(request, username=identifier, password=password)

            if user:
                login(request, user)
                apply_role(user)
                messages.success(request, _("Вход выполнен"))
                return redirect("shop:index")
            else:
                messages.error(request, _("Неверный логин/email или пароль"))
    else:
        form = LoginForm()

    return render(request, "shop/login.html", {"form": form, "already": request.user.is_authenticated})


# ===== ЛОГАУТ =====
@login_required
def logout_view(request):
    id_token = request.session.get("oidc_id_token")

    logout(request)

    if id_token:
        logout_url = (
            f"{settings.OIDC_OP_LOGOUT_ENDPOINT}"
            f"?id_token_hint={id_token}"
            f"&post_logout_redirect_uri=http://localhost:8000/login/?force=1"
        )
        return redirect(logout_url)

    return redirect("/login/?force=1")


# ===== ДОБАВИТЬ ТОВАР =====
@login_required
def product_add(request):

    if request.user.profile.role != "admin":
        messages.error(request, _("Только админ может добавлять товары."))
        return redirect("shop:index")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, _("Товар добавлен"))
            return redirect("shop:index")
    else:
        form = ProductForm()

    return render(request, "shop/product_form.html", {"form": form, "title": _("Добавить товар")})


# ===== ИЗМЕНИТЬ ТОВАР =====
@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user.profile.role != "admin":
        messages.error(request, _("Вы не можете редактировать товар"))
        return redirect("shop:index")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        old_price = product.price
        if form.is_valid():
            updated = form.save(commit=False)
            updated.previous_price = old_price if updated.price < old_price else None
            updated.save()
            messages.success(request, _("Товар обновлён"))
            return redirect("shop:index")
    else:
        form = ProductForm(instance=product)

    return render(request, "shop/product_form.html", {"form": form, "title": _("Редактировать товар")})


# ===== УДАЛИТЬ ТОВАР =====
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user.profile.role != "admin":
        messages.error(request, _("Вы не можете удалить товар"))
        return redirect("shop:index")

    if request.method == "POST":
        try:
            # Delete the associated photo file if it exists
            if product.photo:
                try:
                    product.photo.delete(save=False)
                except Exception:
                    pass  # Ignore file deletion errors
            
            # Delete the product (cascade will handle cart items and wishlist entries)
            product.delete()
            messages.success(request, _("Товар удалён"))
        except Exception as e:
            messages.error(request, f"Ошибка при удалении товара: {str(e)}")
        
        return redirect("shop:index")

    return redirect(f"/?delete={pk}")


# ===== JSON ДЛЯ МОДАЛКИ =====
def product_json(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return JsonResponse({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "manufacturer": product.manufacturer,
        "release_date": product.release_date,
        "weight": str(product.weight),
        "price": str(product.price),
        "previous_price": str(product.previous_price) if product.previous_price else None,
        "photo": product.photo.url if product.photo else "",
    })
# ===== СТАТИСТИКА =====
def stats_view(request):
    """Страница со статистикой и холстом для отрисовки диаграммы."""
    return render(request, "shop/stats.html", {})


def stats_data(request):
    """Возвращает JSON с данными в формате {"items": [{"date": "DD.MM.YYYY", "value": 123}, ...]}.

    Пока возвращаем примерный набор данных (последние 14 дней). Можно заменить на реальные метрики.
    """
    today = timezone.localdate()
    items = []
    # simple deterministic values for demo
    for i in range(13, -1, -1):
        d = today - datetime.timedelta(days=i)
        # value bounces around so the chart looks interesting
        value = 900 + ((d.day * 37) % 300) + (i * 3)
        items.append({
            "date": d.strftime("%d.%m.%Y"),
            "value": value,
        })

    return JsonResponse({"items": items})


def itemuse1_data(request):
    """Возвращает JSON для кругового графика: реальные товары из корзин."""
    from django.db.models import Sum, Count
    
    # Получаем все товары с их количеством в корзинах
    product_stats = CartItem.objects.values('product__name').annotate(
        total_quantity=Sum('quantity'),
        cart_count=Count('cart', distinct=True)
    ).order_by('-total_quantity')[:10]
    
    items = []
    for stat in product_stats:
        if stat['product__name']:
            items.append({
                "name": stat['product__name'],
                "value": int(stat['total_quantity'] or 0)
            })
    
    return JsonResponse({"items": items})


# =========================================================
#                    К О Р З И Н А
# =========================================================

@login_required
def add_to_cart(request, pk):
    """
    Добавление товара в корзину с увеличением количества.
    Возвращает JSON для AJAX запроса.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': _('Пожалуйста, авторизуйтесь')})
    
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    lang_prefix = '/' + request.LANGUAGE_CODE if request.LANGUAGE_CODE else ''
    return JsonResponse({
        'success': True,
        'message': _("Товар '%s' добавлен в корзину") % product.name,
        'cart_url': request.build_absolute_uri(lang_prefix + '/cart/'),
        'quantity': cart_item.quantity,
    })

def cart_state(request):
    if not request.user.is_authenticated:
        return JsonResponse({'items': {}})
    cart, created = Cart.objects.get_or_create(user=request.user)
    items_qs = CartItem.objects.filter(cart=cart, product__isnull=False)
    items_dict = {}
    for item in items_qs:
        items_dict[item.product.id] = item.quantity
    return JsonResponse({'items': items_dict})

def wishlist_state(request):
    from .models import Wishlist
    if not request.user.is_authenticated:
        return JsonResponse({'wishlist_ids': []})
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_ids = list(wishlist.products.values_list('id', flat=True))
    return JsonResponse({'wishlist_ids': wishlist_ids})

@login_required
def view_cart(request):
    """
    Отображение корзины с товарами и суммой.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    items_qs = CartItem.objects.filter(cart=cart, product__isnull=False).select_related("product")

    items = []
    total = 0

    for item in items_qs:
        subtotal = item.product.price * item.quantity
        total += subtotal
        items.append({
            'product': item.product,
            'quantity': item.quantity,
            'subtotal': subtotal,  # <-- добавляем subtotal
        })

    return render(request, "shop/cart.html", {
        "cart": cart,
        "items": items,
        "total": total
    })



@login_required
def cart_remove(request, pk):
    """
    Удаление товара из корзины полностью.
    """
    product = get_object_or_404(Product, pk=pk)
    cart = get_object_or_404(Cart, user=request.user)

    CartItem.objects.filter(cart=cart, product=product).delete()
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': _("%s удалён из корзины") % product.name})
    
    messages.success(request, _("%s удалён из корзины") % product.name)
    return redirect("shop:view_cart")


@login_required
def cart_update_quantity(request, pk, action):
    """
    Увеличение или уменьшение количества товара в корзине.
    action = 'increase' | 'decrease' or 'inc' | 'dec'
    """
    product = get_object_or_404(Product, pk=pk)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if action in ['inc', 'increase']:
        cart_item.quantity += 1
        cart_item.save()
    elif action in ['dec', 'decrease']:
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    # If AJAX request, return JSON with new quantity
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_qty = 0
        try:
            ci = CartItem.objects.get(cart=cart, product=product)
            new_qty = ci.quantity
        except CartItem.DoesNotExist:
            new_qty = 0
        return JsonResponse({'success': True, 'quantity': new_qty})

    return redirect("shop:view_cart")


# =========================================================
#                   А Д М И Н   П А Н Е Л Ь
# =========================================================

@login_required
def admin_panel(request):
    """
    Админ-панель для управления пользователями и их корзинами.
    """
    if request.user.profile.role != "admin":
        messages.error(request, _("У вас нет доступа к админ-панели"))
        return redirect("shop:index")

    # Создаем профили для пользователей, которые их не имеют (например, SSO)
    users = User.objects.all()
    for user in users:
        if not hasattr(user, "profile"):
            Profile.objects.create(user=user)
    
    return render(request, "shop/admin_panel.html", {"users": users})


@login_required
def user_cart(request, user_id):
    """
    Просмотр корзины конкретного пользователя (только для админа).
    """
    if request.user.profile.role != "admin":
        messages.error(request, _("У вас нет доступа"))
        return redirect("shop:index")

    user = get_object_or_404(User, id=user_id)
    cart, created = Cart.objects.get_or_create(user=user)
    items_qs = CartItem.objects.filter(cart=cart, product__isnull=False).select_related("product")

    items = []
    total = 0

    for item in items_qs:
        subtotal = item.product.price * item.quantity
        total += subtotal
        items.append({
            'product': item.product,
            'quantity': item.quantity,
            'subtotal': subtotal,
        })

    return render(request, "shop/user_cart.html", {
        "viewed_user": user,
        "cart": cart,
        "items": items,
        "total": total
    })


@login_required
def toggle_admin_role(request, user_id):
    """
    Переключение админ-роли у пользователя.
    """
    if request.user.profile.role != "admin":
        messages.error(request, "У вас нет доступа")
        return redirect("shop:index")

    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        messages.error(request, _("Вы не можете изменить свою роль"))
        return redirect("shop:admin_panel")

    if user.profile.role == "admin":
        user.profile.role = "user"
        messages.success(request, _("%s больше не администратор") % user.username)
    else:
        user.profile.role = "admin"
        messages.success(request, _("%s теперь администратор") % user.username)
    
    user.profile.save()
    return redirect("shop:admin_panel")


# ===== WISHLIST =====
@login_required
def toggle_wishlist(request, product_id):
    from .models import Wishlist
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        in_wishlist = False
        message = _("Товар удален из избранного")
    else:
        wishlist.products.add(product)
        in_wishlist = True
        message = _("Товар добавлен в избранное")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        lang_prefix = '/' + request.LANGUAGE_CODE if request.LANGUAGE_CODE else ''
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'message': message,
            'wishlist_url': request.build_absolute_uri(lang_prefix + '/wishlist/')
        })
    return redirect('shop:index')


@login_required
def wishlist_view(request):
    from .models import Wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    return render(request, 'shop/wishlist.html', {'products': products})


# ===== ПРОФИЛЬ =====
@login_required
@login_required
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        # Email change with password confirmation
        if action == 'change_email':
            new_email = request.POST.get('new_email', '').strip()
            password = request.POST.get('password_confirm', '').strip()
            
            if not new_email:
                messages.error(request, _("Email не может быть пустым"))
            elif new_email == request.user.email:
                messages.error(request, _("Новый email совпадает со старым"))
            elif User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                messages.error(request, _("Email уже используется"))
            elif not request.user.check_password(password):
                messages.error(request, _("Неверный пароль"))
            else:
                request.user.email = new_email
                request.user.save()
                messages.success(request, _("Email изменен"))
        
        # Change first name
        elif action == 'change_name':
            first_name = request.POST.get('first_name', '').strip()
            request.user.first_name = first_name
            request.user.save()
            messages.success(request, _("Имя изменено"))
        
        # Change last name
        elif action == 'change_lastname':
            last_name = request.POST.get('last_name', '').strip()
            request.user.last_name = last_name
            request.user.save()
            messages.success(request, _("Фамилия изменена"))
        
        # Change password
        elif action == 'change_password':
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            
            if not new_password:
                messages.error(request, _("Пароль не может быть пустым"))
            elif new_password != confirm_password:
                messages.error(request, _("Пароли не совпадают"))
            elif len(new_password) < 6:
                messages.error(request, _("Пароль должен быть минимум 6 символов"))
            else:
                request.user.set_password(new_password)
                request.user.save()
                login(request, request.user)
                messages.success(request, _("Пароль изменен"))
        
        return redirect('shop:profile')
    
    return render(request, 'shop/profile.html', {
        'user': request.user,
    })


