# Create your views here.
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .models import Query, Resolution, StaffProfile, Department, Category
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

def home(request):
    return render(request, "home.html")

def landing(request):
    return render(request, "landing.html")


def staff_register(request):
    departments = Department.objects.all()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        department_name = request.POST.get("department")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
            return redirect("staff_register")

        # Create the user
        username = email.split("@")[0]  # simple username from email
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # Link with department
        try:
            department = Department.objects.get(name=department_name)
        except Department.DoesNotExist:
            messages.error(request, "Invalid department")
            return redirect("staff_register")

        StaffProfile.objects.create(user=user, department=department)

        # Auto login after registration
        # login(request, user)
        # messages.success(request, "Staff account created successfully!")
        return render(request, "staff/registeration.html")

    return render(request, "staff/staff-signup.html", {"departments": departments})


def staff_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # check if a user with this email exists
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("staff_login")

        # authenticate using username + password
        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("admin_dashboard")  # redirect to admin_dashboard
            else:
                return redirect("staff_dashboard")  # redirect to staff dashboard
        else:
            messages.error(request, "Invalid email or password")
            return redirect("staff_login")

    # return render(request, "staff/staff-login.html")
    return render(request, "staff/Staff-login.html")


@login_required
def staff_dashboard(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")  # redirect to admin_dashboard

    # get staff profile and department
    staff_profile = StaffProfile.objects.get(user=request.user)
    department = staff_profile.department

    # filter queries for this staff's department
    queries = Query.objects.filter(department=department).order_by("-created_at")

    # stats
    total_queries = queries.count()
    pending_count = queries.filter(status="pending").count()
    in_progress_count = queries.filter(status="in-progress").count()
    resolved_count = queries.filter(status="resolved").count()

    context = {
        "staff_profile": staff_profile,
        "queries": queries[:5],  # recent 5 queries
        "total_queries": total_queries,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "resolved_count": resolved_count,
    }

    return render(request, "staff/index-staff.html", context)


# Helper: round-robin staff assignment
def assign_staff_round_robin(department):
    staff_members = StaffProfile.objects.filter(department=department).order_by('last_assigned')

    if not staff_members.exists():
        return None  # no staff available

    # pick the first staff in list
    staff = staff_members.first()

    # update last_assigned so next time another staff is picked
    staff.last_assigned = timezone.now()
    staff.save()

    return staff.user


# def submit_query(request):
#     departments = Department.objects.all()

#     if request.method == "POST":
#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         title = request.POST.get("Query")
#         description = request.POST.get("description")
#         category = request.POST.get("category")
#         department_name = request.POST.get("department")  # optional

#         # If department is provided, use it
#         department = None
#         if department_name and department_name != "select":
#             try:
#                 department = Department.objects.get(name=department_name)
#             except Department.DoesNotExist:
#                 messages.error(request, "Invalid department selected.")
#                 return redirect("submit_query")

#         # Otherwise fall back to category → department mapping
#         if not department:
#             department_map = {
#                 "Technical Support": "IT Support",
#                 "Biling Inquiry": "Finance",
#                 "General Question": "Customer Support",
#                 "Feedback": "Marketing/Operation Support",
#             }
#             dept_name = department_map.get(category)

#             if not dept_name:
#                 messages.error(request, "Invalid category selected.")
#                 return redirect("submit_query")

#             try:
#                 department = Department.objects.get(name=dept_name)
#             except Department.DoesNotExist:
#                 messages.error(request, "Department not found.")
#                 return redirect("submit_query")

#         # Assign staff (round-robin)
#         assigned_staff = assign_staff_round_robin(department)

#         # Create query
#         Query.objects.create(
#             user_name=name,
#             user_email=email,
#             title=title,
#             department=department,
#             description=description,
#             status="open",
#             assigned_to=assigned_staff
#         )

#         return render(request, "users/QSubmitted.html")

#     return render(request, "users/Query-Submit-Form.html", {"departments": departments})

def submit_query(request):
    categories = Category.objects.select_related("department").all()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        title = request.POST.get("Query")
        description = request.POST.get("description")
        category_id = request.POST.get("category")

        try:
            category = Category.objects.select_related("department").get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            return redirect("submit_query")

        department = category.department

        # Assign staff (round-robin)
        assigned_staff = assign_staff_round_robin(department)

        # Save query
        Query.objects.create(
            user_name=name,
            user_email=email,
            title=title,
            description=description,
            department=department,
            assigned_to=assigned_staff,
            status="open",
        )

        return render(request, "users/QSubmitted.html")

    return render(request, "users/Query-Submit-Form.html", {"categories": categories})


# helper: check if user is superuser
def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Query stats
    total_queries = Query.objects.count()
    pending_count = Query.objects.filter(status="open").count()
    in_progress_count = Query.objects.filter(status="in_progress").count()
    resolved_count = Query.objects.filter(status="resolved").count()

    recent_queries = Query.objects.all().order_by("-created_at")[:10]

    context = {
        "total_queries": total_queries,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "resolved_count": resolved_count,
        "recent_queries": recent_queries,
    }
    return render(request, "admin-dashboard/Admin-Dashboard.html", context)



@login_required
@user_passes_test(is_admin)
def staff_management(request):
    staff_profiles = StaffProfile.objects.select_related("user", "department")
    departments = Department.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        # Create staff
        if action == "create":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            dept_id = request.POST.get("department")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                department = Department.objects.get(id=dept_id) if dept_id else None
                StaffProfile.objects.create(user=user, department=department)
                messages.success(request, f"Staff {username} created successfully.")

        # Update staff
        elif action == "update":
            staff_id = request.POST.get("staff_id")
            dept_id = request.POST.get("department")
            try:
                profile = StaffProfile.objects.get(id=staff_id)
                if dept_id:
                    profile.department = Department.objects.get(id=dept_id)
                profile.save()
                messages.success(request, f"{profile.user.username}'s department updated.")
            except StaffProfile.DoesNotExist:
                messages.error(request, "Staff not found.")

        # Delete staff
        elif action == "delete":
            staff_id = request.POST.get("staff_id")
            try:
                profile = StaffProfile.objects.get(id=staff_id)
                username = profile.user.username
                profile.user.delete()  # also deletes profile
                messages.success(request, f"Staff {username} deleted.")
            except StaffProfile.DoesNotExist:
                messages.error(request, "Staff not found.")

        return redirect("staff_management")

    context = {
        "staff_profiles": staff_profiles,
        "departments": departments,
    }
    return render(request, "admin-dashboard/staff-management.html", context)


@login_required
@user_passes_test(is_admin)
def department_management(request):
    departments = Department.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            name = request.POST.get("name")
            desc = request.POST.get("description")
            Department.objects.create(name=name, description=desc)
            messages.success(request, f"Department {name} created.")

        elif action == "update":
            dept_id = request.POST.get("dept_id")
            name = request.POST.get("name")
            desc = request.POST.get("description")
            dept = Department.objects.get(id=dept_id)
            dept.name = name
            dept.description = desc
            dept.save()
            messages.success(request, f"Department {name} updated.")

        elif action == "delete":
            dept_id = request.POST.get("dept_id")
            dept = Department.objects.get(id=dept_id)
            dept.delete()
            messages.success(request, "Department deleted.")

        return redirect("department_management")

    return render(request, "admin-dashboard/departments.html", {"departments": departments})


@login_required
@user_passes_test(is_admin)
def query_management(request):
    queries = Query.objects.select_related("department", "assigned_to").order_by("-created_at")
    staff_profiles = StaffProfile.objects.select_related("user", "department")

    if request.method == "POST":
        action = request.POST.get("action")
        query_id = request.POST.get("query_id")
        query = get_object_or_404(Query, id=query_id)

        if action == "update_status":
            status = request.POST.get("status")
            if status in ["open", "in_progress", "resolved"]:
                query.status = status
                query.save()
                messages.success(request, f"Query #{query.id} marked as {status}.")

        elif action == "reassign":
            staff_id = request.POST.get("staff_id")
            profile = StaffProfile.objects.get(id=staff_id)
            query.assigned_to = profile.user
            query.save()
            messages.success(request, f"Query #{query.id} reassigned to {profile.user.username}.")

        elif action == "delete":
            query.delete()
            messages.success(request, "Query deleted.")

        return redirect("query_management")

    return render(request, "admin-dashboard/all-queries.html", {"queries": queries, "staff_profiles": staff_profiles})



def staff_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("staff_login")


@login_required
def staff_profile(request):
    staff_profile = request.user.profile
    departments = Department.objects.all()

    if request.method == "POST":
        # Update basic info
        name = request.POST.get("name")
        email = request.POST.get("email")
        department_id = request.POST.get("department")

        # Split name into first/last
        if name:
            parts = name.split(" ", 1)
            request.user.first_name = parts[0]
            if len(parts) > 1:
                request.user.last_name = parts[1]
        if email:
            request.user.email = email
        request.user.save()

        # Update department
        if department_id:
            staff_profile.department = Department.objects.get(id=department_id)
            staff_profile.save()

        # Change password if provided
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if current_password and new_password and confirm_password:
            if request.user.check_password(current_password):
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # keep user logged in
                    messages.success(request, "Password updated successfully!")
                else:
                    messages.error(request, "New passwords do not match.")
            else:
                messages.error(request, "Current password is incorrect.")

        messages.success(request, "Profile updated successfully!")
        return redirect("staff_dashboard")

    return render(request, "staff/profile.html", {"staff_profile": staff_profile, "departments": departments})


@login_required
def staff_query_detail(request, query_id):
    query = get_object_or_404(Query, id=query_id)

    if request.method == "POST":
        # Update status
        status = request.POST.get("status")
        if status in ["open", "in_progress", "resolved"]:
            query.status = status
            query.save()

        # Add resolution message
        message = request.POST.get("resolution_message")
        if message:
            Resolution.objects.create(query=query, staff=request.user, message=message)

            # optional: send email to user
            from django.core.mail import send_mail
            send_mail(
                subject=f"Resolution for your query #{query.id}",
                message=message,
                from_email="support@sakastrack.com",
                recipient_list=[query.user_email],
            )

        messages.success(request, "Query updated successfully.")
        return redirect("staff_query_detail", query_id=query.id)

    return render(request, "staff/query_detail.html", {"query": query})


def track_query(request):
    query_result = None
    error = None

    if request.method == "POST":
        query_number = request.POST.get("query_number")
        email = request.POST.get("email")

        if query_number:
            query_result = Query.objects.filter(query_number=query_number).first()
        elif email:
            query_result = Query.objects.filter(user_email=email).order_by("-created_at").first()

        if not query_result:
            error = "No query found with the provided details."

    return render(request, "users/track_query.html", {"query_result": query_result, "error": error})
