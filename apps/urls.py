from django.urls import path
from apps.views.customers import CustomerListView, CustomerDebtListView, DebtPaymentView
from apps.views.employees import EmployeeListView, EmployeeAddView, EmployeeUpdateView, EmployeeDeleteView
from apps.views.products import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ExportProductsPDFView, ExportProductsExcelView
from apps.views.purchases import PurchaseListView, AddPurchaseView, PurchaseDetailView, PurchasePDFView, PurchaseCompleteView, PurchaseCancelView
from apps.views.sales import SaleCreateView, SaleHistoryView, SaleDetailView, GetProductView, SaleReceiptPDFView
from apps.views.reports import ReportsView
from apps.views.users import CustomLoginView, CustomLogoutView, ProfileView, CustomPasswordChangeView, DashboardView

urlpatterns = [
    # --- Customers ---
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('<int:customer_id>/debts/', CustomerDebtListView.as_view(), name='customer_debt_list'),
    path('<uuid:debt_pk>/payment/', DebtPaymentView.as_view(), name='debt_payment'),
    # --- Employees ---
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', EmployeeAddView.as_view(), name='employee_add'),
    path('employees/<int:pk>/update/', EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),

        # --- Products ---
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<uuid:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<uuid:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/export/pdf/', ExportProductsPDFView.as_view(), name="export_products_pdf"),
    path('products/export/excel/', ExportProductsExcelView.as_view(), name="export_products_excel"),

        # --- Purchases ---
    path('purchases/', PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/add/', AddPurchaseView.as_view(), name='add_purchase'),
    path('purchases/detail/<uuid:pk>/', PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchases/detail/<uuid:pk>/pdf/', PurchasePDFView.as_view(), name='purchase_pdf'),
    path('purchases/<uuid:pk>/complete/', PurchaseCompleteView.as_view(), name='purchase_complete'),
    path('purchases/<uuid:pk>/cancel/', PurchaseCancelView.as_view(), name='purchase_cancel'),

        # --- Sales ---
    path('sales/create/', SaleCreateView.as_view(), name='sale_create'),
    path('sales/get-product/', GetProductView.as_view(), name='get_product'),
    path('sales/history/', SaleHistoryView.as_view(), name='sale_history'),
    path('sales/history/detail/<uuid:pk>/', SaleDetailView.as_view(), name='sale_history_detail'),
    path('sales/<uuid:sale_id>/chek/', SaleReceiptPDFView.as_view(), name='sale_receipt_pdf'),

        # --- Reports ---
    path('reports/', ReportsView.as_view(), name='reports'),

        # --- Auth & Profile ---
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),

        # --- Dashboard ---
    path('', DashboardView.as_view(), name='dashboard'),
]
