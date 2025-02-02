window.addEventListener('DOMContentLoaded', function(e){
    console.log('hello from admin_crud')

    // Функция для отправки обновленных данных на сервер
    async function updateAchievement(achievementId, field, newValue) {
        try {
          const payload = {}
          payload[field] = newValue // Создаем объект с обновленным полем
          payload.id = achievementId
      
          const response = await fetch(`http://0.0.0.0:8000/admin/achievements/${achievementId}`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload), // Передаем объект в формате JSON
          })
      
          if (!response.ok) {
            throw new Error('Ошибка при обновлении достижения')
          }
      
          const updatedAchievement = await response.json()
          console.log('Обновленное достижение:', updatedAchievement)
        } catch (error) {
          console.error('Ошибка:', error)
        }
      }
    
    // Получаем все элементы с атрибутом data-field
    const editableFields = document.querySelectorAll('[data-field]')
    
    // Добавляем обработчик событий для каждого элемента
    editableFields.forEach(field => {
        field.addEventListener('blur', () => { // Событие 'blur' срабатывает, когда элемент теряет фокус
            const achievementId = Number(field.closest('[data-id]').dataset.id) // Получаем ID достижения
            const fieldName = field.dataset.field // Получаем имя поля (title или description)
            const newValue = field.innerText // Получаем новое значение

            // Вызываем функцию для обновления достижения
            updateAchievement(achievementId, fieldName, newValue)
        })
    })
})