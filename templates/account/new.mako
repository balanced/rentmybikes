<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

<div class="row">
    <div class="span7 box">
        <h1>Create your account</h1>
        <div class="span6 offset1">
        <form method="POST">
            ${ utils.csrf_token_input() | n }
            ${ utils.render_field(account_form.name, class_='span5', autofocus='autofocus') }
            ${ utils.render_field(account_form.email, class_='span5') }
            ${ utils.render_field(account_form.password, class_='span5') }
            <div class="actions">
                <button class="btn btn-inverse">save</button>
            </div>
        </form>
        </div>
    </div>

</div>
