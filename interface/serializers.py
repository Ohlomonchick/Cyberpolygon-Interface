from rest_framework import serializers
from interface.models import Answers, LabLevel, LabTask, User


class AnswerSerializer(serializers.ModelSerializer):
    pnet_login = serializers.CharField(write_only=True, required=False)
    user = serializers.CharField(write_only=True, required=False)
    task = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Answers
        fields = ("user", "lab", "datetime", "pnet_login", "task")

    def validate(self, attrs):
        # Ensure at least one of pnet_login or username is provided
        if not attrs.get('pnet_login') and not attrs.get('user'):
            raise serializers.ValidationError(
                {"non_field_errors": "Either pnet_login or username must be provided."}
            )
        return attrs

    def create(self, validated_data):
        # Extract pnet_login and username
        pnet_login = validated_data.pop('pnet_login', None)
        username = validated_data.pop('user', None)
        lab_task_number = validated_data.pop('task', None)

        # Find the user based on pnet_login or username
        try:
            if pnet_login:
                user = User.objects.get(pnet_login=pnet_login)
            elif username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.get(pnet_login=username)
            else:
                raise serializers.ValidationError(
                    {"non_field_errors": "User could not be identified."}
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": "User with the provided credentials does not exist."}
            )

        task = None
        if lab_task_number:
            try:
                task = LabTask(lab=validated_data['lab'], task_id=lab_task_number).objects.get()
            except LabTask.DoesNotExist:
                raise serializers.ValidationError(
                    {"non_field_errors": "Lab doesn't have task with such number."}
                )

        # Create or update the Answers instance
        answers_instance, created = Answers.objects.update_or_create(
            user=user,
            lab=validated_data['lab'],  # Identify based on lab and user
            lab_task=task,
            defaults={'datetime': validated_data.get('datetime')}
        )
        return answers_instance


class LabLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabLevel
        fields = ['id', 'level_number', 'description']


class LabTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTask
        fields = ['id', 'task_id', 'description']