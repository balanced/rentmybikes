<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

${ utils.bike(listing, hide_button=True) }

<div class="row">
    <div class="span7 box">
        <h1>list your bike</h1>
        <div class="span6 offset1">
            <form method="POST" id="kyc">
                ${ utils.csrf_token_input() | n }
                % if request.user.is_authenticated:
                ${ form(listing_form) }
                % else:
                <p>I already have an account.
                    <a href="${ url_for('login.index', redirect_uri=request.url) }">Sign me in</a>.</p>
                ${ form(guest_listing_form) }
                % endif
                % if not bank_account_form.bank_account_uri.data:
                <fieldset>
                    <legend>Add your bank account <span>(optional)</span></legend>
                    ${ utils.render_field(bank_account_form.account_number) }
                    <div class="control-group">
                        ${ bank_account_form.bank_code.label }
                        ${ bank_account_form.bank_code } <span id="bank-code-result"></span>
                    </div>
                </fieldset>
                % endif
                <div class="actions">
                    <button class="btn btn-inverse">save</button>
                </div>
            </form>
        </div>
    </div>
</div>

<%def name="form(form)">
${ utils.render_field(form.type) }
${ utils.render_field(form.listing_id) }
${ utils.render_field(form.name, class_='span5', autofocus="autofocus") }
${ utils.render_field(form.email, class_='span5') }
% if hasattr(form, 'password'):
${ utils.render_field(form.password, class_='span5') }
% endif
${ utils.render_field(form.street_address, class_='span5') }
${ utils.render_field(form.postal_code, class_='span2') }
${ utils.render_field(form.state) }
${ utils.render_field(form.country_code) }
${ utils.render_field(form.phone_number, class_='span4') }
<div class="control-group">
    <label for="date_of_birth_month">Date of Birth</label>
    ${ form.date_of_birth_month(class_='span1') }
    ${ form.date_of_birth_year(class_='span1') }
</div>
</%def>
