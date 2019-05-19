OPENED = 0
CLOSED = 1
SUBMITTED = 0
ACCEPTED = 1
REJECTED = 2

INNER_PRACTICE = 0
OUTER_PRACTICE = 1
BEFORE_GRAD_PRACTICE = 2

PRACTICE_DIARY_KEY = 'practice_diary'
INNER_INDIVIDUAL_TASK_KEY = 'inner_individual_task'
OUTER_INDIVIDUAL_TASK_KEY = 'outer_individual_task'
INNER_REPORT_TITLE_KEY = 'inner_report_title'
OUTER_REPORT_TITLE_KEY = 'outer_report_title'

BAKALAVR = 0
MAGISTER = 1

INSTITUTE_CURATOR = 0
OUTER_CURATOR = 1


GROUP_TYPE = (
    (BAKALAVR, 'Бакалавриат'),
    (MAGISTER, 'Магистратура'),
)


PROFESSOR_TYPE = (
    (INSTITUTE_CURATOR, 'Куратор от института'),
    (OUTER_CURATOR, 'Производственный куратор'),
)


CONTAINER_STATUS = (
    (OPENED, 'Набор открыт'),
    (CLOSED, 'Набор закрыт')
)

ACTIVITY_TO_CONTAINER_STATUS = (
    (OPENED, 'Прием открыт'),
    (CLOSED, 'Прием закрыт'),
)

REQUEST_STATUS = (
    (SUBMITTED, 'Подана'),
    (ACCEPTED, 'Принята'),
    (REJECTED, 'Отклонена'),
)


PRACTICE_TYPE = (
    (INNER_PRACTICE, 'Практика в лаборатории института'),
    (OUTER_PRACTICE, 'Практика на предприятии'),
    (BEFORE_GRAD_PRACTICE, 'Преддипломная практика'),
)

DOCUMENT_STATUS = (
    (SUBMITTED, 'На проверке'),
    (ACCEPTED, 'Принят'),
    (REJECTED, 'Отклонен'),
)

DOCUMENT_KEYS = (
    (PRACTICE_DIARY_KEY, 'Дневник практики'),
    (INNER_INDIVIDUAL_TASK_KEY, 'Индивидуальное задание (внутренняя практика)'),
    (OUTER_INDIVIDUAL_TASK_KEY, 'Индивидуальное задание (внешняя практика)'),
    (INNER_REPORT_TITLE_KEY, 'Титульный лист отчёта (внутренняя практика)'),
    (OUTER_REPORT_TITLE_KEY, 'Титульный лист отчёта (внешняя практика)'),
)
