from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from utils.helpers import _generate_password
from utils.sms_service import send_welcome_sms
from .models import User, ExhibitionEntry

class ExhibitionLookupSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value):
        # Normalize like bulk script
        digits = ''.join(ch for ch in value if ch.isdigit())
        if digits.startswith('233') and len(digits) >= 12:
            digits = '0' + digits[3:3+9]
        elif len(digits) == 9:
            digits = '0' + digits
        if len(digits) != 10 or not digits.startswith('0'):
            raise serializers.ValidationError('Invalid phone format')
        return digits

class ExhibitionRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    student_id = serializers.CharField(required=False, allow_blank=True, max_length=20)
    program = serializers.CharField(required=False, allow_blank=True, max_length=100)
    year_of_study = serializers.CharField(required=False, allow_blank=True, max_length=20)

    def validate_phone(self, value):
        digits = ''.join(ch for ch in value if ch.isdigit())
        if digits.startswith('233') and len(digits) >= 12:
            digits = '0' + digits[3:3+9]
        elif len(digits) == 9:
            digits = '0' + digits
        if len(digits) != 10 or not digits.startswith('0'):
            raise serializers.ValidationError('Invalid phone format')
        return digits

    def validate(self, attrs):
        # If student_id provided ensure uniqueness
        sid = attrs.get('student_id')
        if sid and User.objects.filter(student_id=sid).exists():
            raise serializers.ValidationError({'student_id': 'Already exists'})
        return attrs

class ExhibitionLookupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ExhibitionLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        exists = ExhibitionEntry.objects.filter(phone_number=phone).exists() or User.objects.filter(phone_number=phone).exists()
        if exists:
            return Response({'status': 'found', 'message': 'Your details are on the exhibition register.'})
        return Response({'status': 'not_found', 'message': 'No record found. Please provide details to register.'})

class ExhibitionRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ExhibitionRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        if ExhibitionEntry.objects.filter(phone_number=phone).exists() or User.objects.filter(phone_number=phone).exists():
            return Response({'status': 'exists', 'message': 'Phone already on register.'}, status=status.HTTP_200_OK)
        data = serializer.validated_data
        ExhibitionEntry.objects.create(
            phone_number=phone,
            first_name=data['first_name'].title(),
            last_name=data['last_name'].title(),
            student_id=data.get('student_id',''),
            program=data.get('program',''),
            year_of_study=data.get('year_of_study',''),
            source='self_submitted'
        )
        return Response({'status': 'created', 'message': 'Submitted for verification.'}, status=status.HTTP_201_CREATED)


User = get_user_model()

class ExhibitionPendingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_ec_member or request.user.is_staff):
            return Response({'detail': 'Forbidden'}, status=403)
        pending = ExhibitionEntry.objects.filter(is_verified=False).order_by('-created_at')[:500]
        data = [
            {
                'id': str(e.id),
                'student_id': e.student_id,
                'first_name': e.first_name,
                'last_name': e.last_name,
                'phone_number': e.phone_number,
                'program': e.program,
                'year_of_study': e.year_of_study,
                'source': e.source,
            }
            for e in pending
        ]
        return Response({'pending': data})


class ExhibitionVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not (request.user.is_ec_member or request.user.is_staff):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            entry = ExhibitionEntry.objects.get(id=user_id, is_verified=False)
        except ExhibitionEntry.DoesNotExist:
            return Response({'detail': 'Entry not found or already verified'}, status=404)

        entry.is_verified = True
        entry.verified_by = request.user
        from django.utils import timezone
        entry.verified_at = timezone.now()
        entry.save()
        return Response({'status': 'verified', 'entry_id': str(entry.id)})

class ExhibitionPromoteVerifiedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (request.user.is_ec_member or request.user.is_staff):
            return Response({'detail': 'Forbidden'}, status=403)
        promoted = []
        for entry in ExhibitionEntry.objects.filter(is_verified=True, user__isnull=True)[:500]:
            # Skip if phone already used
            if User.objects.filter(phone_number=entry.phone_number).exists():
                continue
            # Generate student id if missing
            sid = entry.student_id or f"EXH{User.objects.count()+1:05d}"
            user = User(
                username=sid,
                student_id=sid,
                first_name=entry.first_name,
                last_name=entry.last_name,
                phone_number=entry.phone_number,
                program=entry.program,
                year_of_study=entry.year_of_study,
                hall=entry.hall or ''
            )
            raw_password = _generate_password()
            user.set_password(raw_password)
            user.can_vote = True
            user.changed_password = False
            user.save()
            entry.user = user
            entry.save(update_fields=['user'])
            if user.phone_number:
                try:
                    send_welcome_sms(user, raw_password, async_send=True)
                except Exception:
                    pass
            promoted.append({'student_id': user.student_id, 'phone': user.phone_number})
        return Response({'promoted': promoted, 'count': len(promoted)})
