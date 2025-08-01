from django.core.management.base import BaseCommand
from django.db.models.signals import post_save, post_delete
from interface.models import Competition, TeamCompetition, Competition2User, TeamCompetition2Team


class Command(BaseCommand):
    help = 'Удаляет все competitions и teamCompetitions из базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтвердить удаление без дополнительных запросов',
        )

    def handle(self, *args, **options):
        # Отключаем сигналы, которые могут вызвать ошибки при удалении
        self.stdout.write('Отключение сигналов...')
        
        # Сохраняем оригинальные сигналы
        original_post_save_receivers = post_save.receivers[:]
        original_post_delete_receivers = post_delete.receivers[:]
        
        # Очищаем все сигналы для наших моделей
        post_save.receivers = []
        post_delete.receivers = []
        
        self.stdout.write(self.style.SUCCESS('Сигналы отключены'))

        # Подсчитываем количество записей для удаления
        competitions_count = Competition.objects.count()
        team_competitions_count = TeamCompetition.objects.count()
        competition_users_count = Competition2User.objects.count()
        team_competition_teams_count = TeamCompetition2Team.objects.count()

        self.stdout.write(
            self.style.WARNING(
                f'Найдено записей для удаления:\n'
                f'- Competitions: {competitions_count}\n'
                f'- TeamCompetitions: {team_competitions_count}\n'
                f'- Competition2User: {competition_users_count}\n'
                f'- TeamCompetition2Team: {team_competition_teams_count}\n'
                f'Всего: {competitions_count + team_competitions_count + competition_users_count + team_competition_teams_count}'
            )
        )

        if not options['confirm']:
            confirm = input('Вы уверены, что хотите удалить все эти записи? (yes/no): ')
            if confirm.lower() not in ['yes', 'y', 'да', 'д']:
                self.stdout.write(self.style.ERROR('Операция отменена.'))
                return

        try:
            # Удаляем связанные записи
            self.stdout.write('Удаление Competition2User...')
            Competition2User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Удалено {competition_users_count} записей Competition2User'))

            self.stdout.write('Удаление TeamCompetition2Team...')
            TeamCompetition2Team.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Удалено {team_competition_teams_count} записей TeamCompetition2Team'))

            # Удаляем основные модели
            self.stdout.write('Удаление TeamCompetition...')
            TeamCompetition.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Удалено {team_competitions_count} записей TeamCompetition'))

            self.stdout.write('Удаление Competition...')
            Competition.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Удалено {competitions_count} записей Competition'))

            self.stdout.write(
                self.style.SUCCESS(
                    'Все competitions и teamCompetitions успешно удалены из базы данных!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при удалении: {str(e)}')
            )
        finally:
            # Восстанавливаем сигналы
            post_save.receivers = original_post_save_receivers
            post_delete.receivers = original_post_delete_receivers 