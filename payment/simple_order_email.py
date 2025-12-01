# payment/simple_order_email.py
from django.core.mail import send_mail
from django.conf import settings
from payment.models import Order, OrderItem

def send_simple_order_email():
    """
    Simple function to send email with the last order
    Call this after creating a new order
    """
    try:
        # Get the last order
        last_order = Order.objects.last()
        
        if not last_order:
            print("No orders found")
            return False
        
        # Get order items
        order_items = OrderItem.objects.filter(order=last_order)
        
        # Build simple email content
        subject = f"New Order #{last_order.id}"
        
        message = f"""
New Order Received!

Order #{last_order.id}
Customer: {last_order.full_name}
Email: {last_order.email}
Total: ${last_order.amount_paid}
Date: {last_order.date_ordered}

Shipping Address:
{last_order.shipping_address}

Order Items:
"""
        
        # Add each item to the message
        for item in order_items:
            item_total = item.quantity * item.price
            message += f"- {item.product.name} x {item.quantity} = ${item_total}\n"
        
        message += f"\nGrand Total: ${last_order.amount_paid}"
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['amine.majdoub02@gmail.com'],  # Your email
            fail_silently=False,
        )
        
        print(f"Simple order email sent for order #{last_order.id}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False