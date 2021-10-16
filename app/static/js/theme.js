'use strict';

document.addEventListener('DOMContentLoaded', function () {
    // ------------------------------------------------------- //
    // Sidebar Functionality
    // ------------------------------------------------------    //

    const sbToggleBtn = document.getElementById('toggle-btn'),
          mainContent = document.getElementById('main-content'),
          sideNavbar  = document.querySelector('.side-navbar'),
          innerContent = document.querySelector('.content-inner'),
          smBrand = document.querySelector('.navbar-header .brand-small'),
          lgBrand = document.querySelector('.navbar-header .brand-big');


    if (sideNavbar) {
        sbToggleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            this.classList.toggle('active');


            sideNavbar.classList.toggle('shrinked');
            innerContent.classList.toggle('active');
            mainContent.classList.toggle('col-xl-10');
            mainContent.classList.toggle('col-xs-12');
            mainContent.classList.toggle('col');
            document.dispatchEvent(new Event('sidebarChanged'));
        });
    }
    // ------------------------------------------------------- //
    // Material Inputs
    // ------------------------------------------------------ //

    let materialInputs = document.querySelectorAll('input.input-material');
    let materialLabel = document.querySelectorAll('label.label-material');

    // activate labels for prefilled values
    let filledMaterialInputs = Array.from(materialInputs).filter(function (input) {
        return input.value !== '';
    });
    filledMaterialInputs.forEach(input => input.parentElement.lastElementChild.setAttribute('class', 'label-material active'));

    // move label on focus
    materialInputs.forEach((input) => {
        input.addEventListener('focus', function () {
            input.parentElement.lastElementChild.setAttribute('class', 'label-material active');
        });
    });

    // remove/keep label on blur
    materialInputs.forEach((input) => {
        input.addEventListener('blur', function () {
            if (input.value !== '') {
                input.parentElement.lastElementChild.setAttribute('class', 'label-material active');
            } else {
                input.parentElement.lastElementChild.setAttribute('class', 'label-material');
            }
        });
    });


    function bsValidationBehavior(errorInputs, form) {
        function watchError() {
            errorInputs.forEach((input) => {
                if (input.classList.contains('js-validate-error-field')) {
                    input.classList.add('is-invalid');
                    input.classList.remove('is-valid');
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
        }
        watchError();
    }

    // ------------------------------------------------------- //
    // Login Form Validation
    // ------------------------------------------------------ //
    let loginForm = document.querySelector('.login-form');
    if (loginForm) {
        new window.JustValidate('.login-form', {
            rules: {
                loginUsername: {
                    required: true,
                    email: true
                },
                loginPassword: {
                    required: true,
                },
            },
            messages: {
                loginUsername: 'Please enter a valid email',
                loginPassword: 'Please enter your password'
            },
            invalidFormCallback: function () {
                let errorInputs = document.querySelectorAll('.login-form input[required]');
                bsValidationBehavior(errorInputs, loginForm);
                loginForm.addEventListener('keyup', () => bsValidationBehavior(errorInputs, loginForm))
            },
        });
    }

    const profileCountryChoices = document.querySelector('.profile-country-choices');
    if (profileCountryChoices) {
        const countryChoices = new Choices(profileCountryChoices, {
            searchEnabled: false,
            placeholder: false,
            callbackOnInit: () => injectClassess(profileCountryChoices)
        });
    }


});
