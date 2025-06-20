function togglePasswordVisibility() {
          const passwordField = document.getElementById('password') || document.getElementById('reg-password');
          const showPasswordCheckbox = document.getElementById('showPassword');
          passwordField.type = showPasswordCheckbox.checked ? 'text' : 'password';
} 

function togglePasswordVisibility2() {
  const passwordField = document.getElementById('reg-password');
  const showPasswordCheckbox = document.getElementById('showPassword2');
  passwordField.type = showPasswordCheckbox.checked ? 'text' : 'password';
} 


function showForm(formId) {
    document.querySelectorAll('.form-container').forEach(form => form.classList.remove('active'));
    document.getElementById(formId).classList.add('active');
}
    