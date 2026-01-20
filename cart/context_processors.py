from .models import Cart

def cart_count(request):
    count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.get_total_items()
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()
        if cart:
            count = cart.get_total_items()

    return {'cart_count': count}
