from django.shortcuts import render
import io
import qrcode
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, request
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Family, Guest
from django.db.models import Sum
from .forms import FamilyForm

def invitation_view(request, token):
    family = get_object_or_404(Family, id=token)

    if request.method == 'POST':
        if family.is_locked:
            return redirect('invitation_view', token=family.id)

        action = request.POST.get('action')  # 'confirm' o 'decline'
        
        if action == 'decline':
            family.status = 'DECLINED'
            family.confirmed_tickets = 0
            family.is_locked = True
            family.guests.all().delete()
            family.save()
            return redirect('invitation_view', token=family.id)

        # Si confirma asistencia
        guest_names = request.POST.getlist('guest_names[]')
        guest_names = [name.strip() for name in guest_names if name.strip()]
        
        if 0 < len(guest_names) <= family.assigned_tickets:
            family.guests.all().delete()
            for name in guest_names:
                Guest.objects.create(family=family, full_name=name)
            
            family.confirmed_tickets = len(guest_names)
            family.status = 'CONFIRMED'
            family.is_locked = True
            family.save()

        return redirect('invitation_view', token=family.id)

    return render(request, 'rsvp/invitation.html', {'family': family})


def qr_code_view(request, token):
    family = get_object_or_404(Family, id=token)
    qr_data = request.build_absolute_uri(f"/staff/checkin/?token={family.id}")
    qr_img = qrcode.make(qr_data)
    
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')



def checkin_dashboard(request):
    token_query = request.GET.get('token', '')
    search_query = request.GET.get('q', '')

    # Permitir acceso directo por token, o requerir sesión si no viene token
    if not token_query and not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.get_full_path())

    family = None
    if token_query:
        family = Family.objects.filter(id=token_query).first()
    elif search_query:
        family = Family.objects.filter(name__icontains=search_query).first()

    # Traemos todas las familias ordenadas por nombre con sus invitados precargados
    all_families = Family.objects.all().prefetch_related('guests').order_by('name')

    return render(request, 'rsvp/checkin.html', {
        'family': family,
        'search_query': search_query,
        'all_families': all_families,
    })


def toggle_guest_checkin(request, guest_id):
    if request.method == 'POST':
        guest = get_object_or_404(Guest, id=guest_id)
        guest.has_checked_in = not guest.has_checked_in
        guest.check_in_time = timezone.now() if guest.has_checked_in else None
        guest.save()
        return JsonResponse({'status': 'ok', 'checked_in': guest.has_checked_in})
    return JsonResponse({'status': 'error'}, status=400)



def couples_dashboard(request):
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('couples_dashboard')
    else:
        form = FamilyForm()

    families = Family.objects.all().order_by('-created_at')

    total_assigned = families.aggregate(Sum('assigned_tickets'))['assigned_tickets__sum'] or 0
    total_confirmed = families.aggregate(Sum('confirmed_tickets'))['confirmed_tickets__sum'] or 0
    confirmed_count = families.filter(status='CONFIRMED').count()
    pending_count = families.filter(status='PENDING').count()
    declined_count = families.filter(status='DECLINED').count()

    family_cards = []
    host = request.get_host()
    scheme = request.scheme

    for f in families:
        clean_phone = f.contact_phone.replace('+', '').replace(' ', '').replace('-', '') if f.contact_phone else ''
        invitation_link = f"{scheme}://{host}/invitacion/{f.id}/"
        wa_text = f"¡Hola {f.name}! Queremos compartir nuestro día especial contigo. Por favor confirma tus boletos aquí: {invitation_link}"
        wa_url = f"https://wa.me/{clean_phone}?text={wa_text.replace(' ', '%20')}" if clean_phone else None

        family_cards.append({
            'obj': f,
            'wa_url': wa_url,
            'invitation_link': invitation_link
        })

    return render(request, 'rsvp/couples_dashboard.html', {
        'form': form,
        'family_cards': family_cards,
        'total_families': families.count(),
        'total_assigned': total_assigned,
        'total_confirmed': total_confirmed,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'declined_count': declined_count,
    })


def edit_family(request, family_id):
    family = get_object_or_404(Family, id=family_id)
    if request.method == 'POST':
        form = FamilyForm(request.POST, instance=family)
        if form.is_valid():
            # Si le cambian boletos y quieren permitir que vuelva a editar su asistencia:
            unlock = request.POST.get('unlock_rsvp')
            if unlock == '1':
                family.is_locked = False
                family.status = 'PENDING'
            form.save()
            return redirect('couples_dashboard')
    else:
        form = FamilyForm(instance=family)

    return render(request, 'rsvp/edit_family.html', {
        'form': form,
        'family': family
    })


def delete_family(request, family_id):
    if request.method == 'POST':
        family = get_object_or_404(Family, id=family_id)
        family.delete()
    return redirect('couples_dashboard')