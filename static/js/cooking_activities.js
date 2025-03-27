function updateRecipeInfo() {
    const recipeSelect = document.getElementById('recipe_type');
    const recipeInfo = document.getElementById('recipe_info');
    const dishNameInput = document.getElementById('dish_name');
    const cookingTimeInput = document.getElementById('cooking_time');
    const temperatureInput = document.getElementById('temperature');

    if (recipeSelect.value && recipeSelect.value !== 'custom') {
        fetch(`/get_cooking_guide/${recipeSelect.value}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('recommended_temp').textContent = data.recommended_temp;
                document.getElementById('recommended_time').textContent = data.cooking_time;
                document.getElementById('cooking_tips').textContent = data.tips;
                
                dishNameInput.value = data.name;
                cookingTimeInput.value = data.cooking_time;
                temperatureInput.value = data.recommended_temp;
                
                recipeInfo.classList.remove('hidden');
            })
            .catch(error => {
                console.error('Error fetching recipe info:', error);
                alert('Failed to fetch recipe information. Please try again.');
            });
    } else {
        recipeInfo.classList.add('hidden');
        dishNameInput.value = '';
        cookingTimeInput.value = '';
        temperatureInput.value = '';
    }
}

function updateStep(activityIndex, step) {
    fetch(`/update_step/${activityIndex}/${step}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Instead of reloading the page, update the UI directly
                const stepItems = document.querySelectorAll('.cooking-steps li');
                stepItems.forEach((item, index) => {
                    if (index <= step) {
                        item.classList.add('completed-step');
                    }
                    // Remove all existing step buttons
                    const existingBtn = item.querySelector('.step-btn');
                    if (existingBtn) {
                        existingBtn.remove();
                    }
                });

                // Add button to the next step if it exists
                if (step + 1 < stepItems.length) {
                    const nextStep = stepItems[step + 1];
                    const newBtn = document.createElement('button');
                    newBtn.className = 'step-btn';
                    newBtn.textContent = 'Complete Step';
                    newBtn.onclick = () => updateStep(activityIndex, step + 1);
                    nextStep.appendChild(newBtn);
                }
            }
        })
        .catch(error => {
            console.error('Error updating step:', error);
            alert('Failed to update step. Please try again.');
        });
}

function addActivity(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/add_activity', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error adding activity:', error);
        alert('Failed to add activity. Please try again.');
    });

    return false;
}

function completeActivity(index) {
    fetch(`/complete_activity/${index}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Update UI directly instead of reloading
                const activityCard = document.querySelector(`.activity-card:nth-child(${index + 1})`);
                if (activityCard) {
                    activityCard.classList.add('completed');
                    const statusSpan = activityCard.querySelector('.activity-status');
                    if (statusSpan) {
                        statusSpan.textContent = 'Completed';
                    }
                    // Remove complete button
                    const completeBtn = activityCard.querySelector('.complete-btn');
                    if (completeBtn) {
                        completeBtn.remove();
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error completing activity:', error);
            alert('Failed to complete activity. Please try again.');
        });
}

