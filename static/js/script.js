document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patientForm');
    const steps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    let currentStep = 0;

    goToStep(0);

    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (validateStep(currentStep)) {
                goToStep(currentStep + 1);
            }
        });
    });

    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            goToStep(currentStep - 1);
        });
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateStep(currentStep)) {
            alert('Please complete all required fields before submitting.');
            return;
        }

        const formData = {
            client_name: document.getElementById('ownerName').value,
            client_phone_number: document.getElementById('ownerPhone').value,
            client_email: document.getElementById('ownerEmail').value,
            client_location: document.getElementById('ownerAddress').value,
            patient_name: document.getElementById('petName').value,
            species: document.getElementById('petSpecies').value,
            breed: document.getElementById('petBreed').value,
            age: document.getElementById('petAge').value,
            gender: document.getElementById('petGender').value,
            weight: document.getElementById('weight').value,
            temperature: document.getElementById('temperature').value,
            heart_rate: document.getElementById('heartRate').value,
            crt: document.getElementById('capillaryRefill').value,
            mm: document.getElementById('mucousMembrane').value,
            neutering_status: document.getElementById('neutering_status').value,
            physicalExamNotes: document.getElementById('physicalExamNotes').value,
            presenting_complaint: document.getElementById('presentingComplaint').value,
            diagnosis: document.getElementById('diagnosis').value,
            treatment_given: document.getElementById('treatment').value,
            prescriptions: document.getElementById('prescriptions').value,
            follow_up_required: document.getElementById('followUp').value
        };

        try {
            const submitBtn = document.getElementById('completeRegistration');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin style="font-size: 0.9em; margin-right: 8px;"></i> Processing...';

            const response = await fetch("/new_case", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name="csrf_token"]').value
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Submission failed');
            }

            document.getElementById('reviewSection').style.display = 'none';
            document.getElementById('successMessage').style.display = 'block';
            
        } catch (error) {
            console.error('Error:', error);
            alert('Submission failed: ' + error.message);
            
            const submitBtn = document.getElementById('completeRegistration');
            submitBtn.disabled = false;
            submitBtn.textContent = 'CONFIRM';
        }
    });

    function goToStep(step) {
        if (step < 0 || step >= steps.length) return;

        steps.forEach(stepElement => {
            stepElement.classList.remove('active');
        });

        steps[step].classList.add('active');

        progressSteps.forEach((progressStep, index) => {
            if (index < step) {
                progressStep.classList.add('completed');
                progressStep.classList.remove('active');
            } else if (index === step) {
                progressStep.classList.add('active');
                progressStep.classList.remove('completed');
            } else {
                progressStep.classList.remove('active', 'completed');
            }
        });

        if (step === 4) {
            updateReviewSection();
        }

        currentStep = step;
    }

    function validateStep(step) {
        if (step < 0 || step >= steps.length) return false;
        
        const currentStepElement = steps[step];
        let isValid = true;
        
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            const isEmpty = !field.value.trim();
            const errorMsg = field.parentNode.querySelector('.error-message');
            
            if (isEmpty) {
                field.style.borderColor = 'red';
                if (!errorMsg) {
                    const err = document.createElement('div');
                    err.className = 'error-message';
                    err.textContent = 'This field is required';
                    field.parentNode.appendChild(err);
                }
                isValid = false;
            } else {
                field.style.borderColor = '#ddd';
                if (errorMsg) {
                    errorMsg.remove();
                }
            }
        });
        
        return isValid;
    }

    function updateReviewSection() {
        document.getElementById('review-ownerName').textContent = document.getElementById('ownerName').value;
        document.getElementById('review-ownerPhone').textContent = document.getElementById('ownerPhone').value;
        document.getElementById('review-ownerEmail').textContent = document.getElementById('ownerEmail').value;
        document.getElementById('review-ownerAddress').textContent = document.getElementById('ownerAddress').value;
        
        document.getElementById('review-petName').textContent = document.getElementById('petName').value;
        document.getElementById('review-petSpecies').textContent = 
            document.getElementById('petSpecies').options[document.getElementById('petSpecies').selectedIndex].text;
        document.getElementById('review-petBreed').textContent = document.getElementById('petBreed').value || 'N/A';
        document.getElementById('review-petAge').textContent = document.getElementById('petAge').value || 'N/A';
        document.getElementById('review-petGender').textContent = 
            document.getElementById('petGender').options[document.getElementById('petGender').selectedIndex].text;
        
        document.getElementById('review-weight').textContent = document.getElementById('weight').value || 'N/A';
        document.getElementById('review-temperature').textContent = document.getElementById('temperature').value || 'N/A';
        document.getElementById('review-heartRate').textContent = document.getElementById('heartRate').value || 'N/A';
        document.getElementById('review-capillaryRefill').textContent = document.getElementById('capillaryRefill').value || 'N/A';
        document.getElementById('review-mucousMembrane').textContent = document.getElementById('mucousMembrane').value || 'N/A';
        document.getElementById('review-neutering_status').textContent = document.getElementById('neutering_status').value || 'N/A';
        document.getElementById('review-physicalExamNotes').textContent = document.getElementById('physicalExamNotes').value || 'N/A';
        
        document.getElementById('review-presentingComplaint').textContent = document.getElementById('presentingComplaint').value || 'N/A';
        document.getElementById('review-diagnosis').textContent = document.getElementById('diagnosis').value || 'N/A';
        document.getElementById('review-treatment').textContent = document.getElementById('treatment').value || 'N/A';
        document.getElementById('review-prescriptions').textContent = document.getElementById('prescriptions').value || 'N/A';
        document.getElementById('review-followUp').textContent = document.getElementById('followUp').value || 'N/A';
    }

    window.resetForm = function() {
        form.reset();
        document.getElementById('successMessage').style.display = 'none';
        document.getElementById('reviewSection').style.display = 'block';

        document.querySelectorAll('[required]').forEach(field => {
            field.style.borderColor = '';
            const errorMsg = field.parentNode.querySelector('.error-message');
            if (errorMsg) errorMsg.remove();
        });
        
        currentStep = 0;
        goToStep(0);
    };
});