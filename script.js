function togglePasswordVisibility() {
          const passwordField = document.getElementById('password');
          const showPasswordCheckbox = document.getElementById('showPassword');
          passwordField.type = showPasswordCheckbox.checked ? 'text' : 'password';
} 
