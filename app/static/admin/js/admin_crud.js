window.addEventListener('DOMContentLoaded', function(e){
    console.log('hello from admin_crud')

    // Обновление данных через редактируемые поля
    // =============================================
    async function updateAchievement() {
        // Получаем все элементы с атрибутом data-field
        const editableFields = document.querySelectorAll('[data-field]')
        let currentValue = ''

        // Сохраняем текущее значение поля для проверки на изменяемость
        editableFields.forEach(field => {
            field.addEventListener('focus', (e) => currentValue = field.innerText)
        })
        
        // Добавляем обработчик событий для каждого элемента
        editableFields.forEach(field => {
            field.addEventListener('blur', async (e) => { // Событие 'blur' срабатывает, когда элемент теряет фокус
                const tableName = field.closest('[data-table]').dataset.table // Получаем название таблицы
                const objectId = Number(field.closest('[data-id]').dataset.id) // Получаем ID достижения
                const fieldName = field.dataset.field // Получаем имя поля (title или description)
                const newValue = field.innerText // Получаем новое значение

                if (newValue === currentValue) {
                    console.log("Данное поле не изменялось...")
                    return
                }
                // Вызываем функцию для обновления достижения
                const payload = {}
                // Создаем объект с обновленным полем
                payload.id = objectId
                payload.table = tableName
                payload[fieldName] = newValue

                try {
                const response = await fetch(`http://0.0.0.0:8000/admin/${tableName}/${objectId}`, {
                    method: 'PATCH',
                    headers: {
                    'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload), // Передаем объект в формате JSON
                })
                if (!response.ok) {
                    throw new Error(`Ошибка при обновлении объекта ${objectId} в таблице ${tableName}`)
                }
                const updatedObject = await response.json()
                console.log('Обновленно успешно!', updatedObject)
                } catch (error) {
                console.error('Ошибка:', error)
                }
            })
        })
    }

    updateAchievement()

    // Добавление нового инстанса
    // =============================================
    document.querySelectorAll('.js-add-instance').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault()

            const currentButton = e.target

            const payload = {}

            payload.section_id = Number(currentButton.closest('[data-table="sections"]').dataset.id)
            payload.table_name = currentButton.dataset.table
            payload.title = null
            payload.description = null
            payload.image_desktop = null
            payload.image_mobile = null
            payload.image_alt = null
            payload.button_text = null
            payload.button_url = null
            payload.order_value = 0

            console.log(payload)

            try {
                const response = await fetch(`http://0.0.0.0:8000/admin/sections/${payload.table_name}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                })
                const result = await response.json()
                if (!response.ok) {
                    throw new Error(`Произошла ошибка при создании экземпляра в сущности ${payload.table_name}`)
                }
                console.log('Обновленно успешно!', result)
            } catch (error) {
                alert('Ошибка при создании экземпляра: ' + error.message)
            }
        })
    })

    // Загрузка картинки
    // =============================================
    document.querySelectorAll('.js-upload-image').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault()

            const formData = new FormData(form)
            formData.append("entity_name", e.target.closest('[data-table]').dataset.table)
            formData.append("entity_id", Number(e.target.closest('[data-id]').dataset.id))
            formData.append("image_type", e.target.image_type.value)
            
            try {
                const response = await fetch(`http://0.0.0.0:8000/admin/images`, {
                    method: 'POST',
                    body: formData
                })
                const result = await response.json()
                if (!response.ok) {
                    throw new Error(`Произошла ошибка при обновлении поля ${entity_id} в таблице ${entity_name}`)
                }
                console.log('Обновленно успешно!', result)
            } catch (error) {
                alert('Ошибка при загрузке изображения: ' + error.message)
            }
        })
    })

    // Удаление картинки
    // =============================================
    document.querySelectorAll('.js-update-image').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault()

            const payload = {}
            const currentButton = e.target
            payload.image_type = currentButton.dataset.type
            payload.image_action = currentButton.dataset.action
            payload.image_src = currentButton.dataset.src
            payload.entity_id = Number(currentButton.closest('[data-id]').dataset.id)
            payload.entity_name = currentButton.closest('[data-table]').dataset.table
            
            console.log(payload)

            try {
                const response = await fetch(`http://0.0.0.0:8000/admin/images/${payload.entity_name}/${payload.entity_id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                })
                if (!response.ok) {
                    throw new Error(`Произошла ошибка при обновлении поля ${payload.entity_id} в таблице ${payload.entity_name}`)
                }
                const success = await response.json()
                console.log('Обновленно успешно!', success)
            } catch (error) {
                alert('Ошибка при загрузке изображения: ' + error.message)
            }

        })
    })
})
