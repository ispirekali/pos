from datetime import datetime, timedelta
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField, F, IntegerField, Avg
from django.db.models.functions import Coalesce
from django.shortcuts import render
from products.models import Product, Category
from sales.models import Sale, SaleDetail
import json



@login_required(login_url="/accounts/login/")
def index(request):
    today = date.today()
    year = today.year
    monthly_earnings = []
    monthly_sales = []
    monthly_profits = []

    sale_details = SaleDetail.objects.all()
    daily_profit = sale_details.filter(sale__date__date=today).aggregate(Sum('profit'))['profit__sum']
    weekly_profit = sale_details.filter(sale__date__gte=datetime.today() - timedelta(days=7)).aggregate(Sum('profit'))['profit__sum']
    monthly_profit = sale_details.filter(sale__date__gte=datetime.today() - timedelta(days=30)).aggregate(Sum('profit'))['profit__sum']
    annual_profit = sale_details.aggregate(Sum('profit'))['profit__sum']

    # Calculate earnings and profits per month
    for month in range(1, 13):
        sales = Sale.objects.filter(created_at__year=year, created_at__month=month)
        earning = sales.aggregate(total_variable=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
        buying_price = sales.aggregate(total_variable=Coalesce(Sum(F('saledetail__product__buying_price') * F('saledetail__quantity')), 0.0, output_field=FloatField())).get('total_variable')
        profit = earning - buying_price  # Calculate the profit
        monthly_earnings.append({
            'earning': earning,
            'profit': profit
        })
        monthly_sales.append(sales.count())
        monthly_profits.append(profit)

    # Calculate annual earnings and profit
    sales = Sale.objects.filter(created_at__year=year)
    annual_earnings = sales.aggregate(total_variable=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
    annual_buying_price = sales.aggregate(total_variable=Coalesce(Sum(F('saledetail__product__buying_price') * F('saledetail__quantity')), 0.0, output_field=FloatField())).get('total_variable')
    annual_profit = annual_earnings - annual_buying_price
    annual_earnings = format(annual_earnings, '.2f')
    annual_profit = format(annual_profit, '.2f')

    # Calculate daily and weekly sales
    seven_days_ago = today - timedelta(days=7)
    today_sales = Sale.objects.filter(created_at=today).count()
    weekly_sales = Sale.objects.filter(created_at__range=[seven_days_ago, today]).count()

    # Calculate average earnings per month
    avg_month = Sale.objects.filter(created_at__year=year).aggregate(
        avg_variable=Coalesce(Avg(F('grand_total')), 0.0, output_field=FloatField())).get('avg_variable')
    avg_month = format(avg_month, '.2f')


    # Top selling products
    top_products = Product.objects.annotate(quantity_sum=Sum(
        'saledetail__quantity')).order_by('-quantity_sum')[:3]

    top_products_names = []
    top_products_quantity = []

    for p in top_products:
        top_products_names.append(p.name)
        top_products_quantity.append(p.quantity_sum)


     # Calculate daily sales and profits
    today_sales = Sale.objects.filter(date__date=today).aggregate(
        total_sales=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_sales')
    today_profits = SaleDetail.objects.filter(sale__date__date=today).aggregate(
        total_profits=Coalesce(Sum(F('profit')), 0.0, output_field=FloatField())).get('total_profits')
    today_sales = format(today_sales, '.2f')
    today_profits = format(today_profits, '.2f')


     # Calculate weekly sales and profits
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_sales = Sale.objects.filter(created_at__range=[start_of_week, end_of_week]).aggregate(
        total_sales=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_sales')
    weekly_profits = SaleDetail.objects.filter(sale__date__range=[start_of_week, end_of_week]).aggregate(
        total_profits=Coalesce(Sum(F('profit')), 0.0, output_field=FloatField())).get('total_profits')
    weekly_sales = format(weekly_sales, '.2f')
    weekly_profits = format(weekly_profits, '.2f')


    context = {
        "active_icon": "dashboard",
        "products": Product.objects.all().count(),
        "categories": Category.objects.all().count(),
        "annual_earnings": annual_earnings,
        "annual_profit": annual_profit,
        "monthly_earnings": json.dumps(monthly_earnings),
        "monthly_sales": json.dumps(monthly_sales),
        "monthly_profit": monthly_profit,
        "avg_month": avg_month,
        "top_products_names": json.dumps(top_products_names),
        "top_products_names_list": top_products_names,
        "top_products_quantity": json.dumps(top_products_quantity),
        "today_sales": today_sales,
        "today_profits": today_profits,
        "weekly_sales": weekly_sales,
        "weekly_profit": weekly_profit,

        'sales': sales,
        'daily_profit': daily_profit,
    }
    return render(request, "pos/index.html", context)
