<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

<div class="row">
    <div class="span7 box">
        <h1>Log in</h1>
        <div class="span6 offset1">
            <form method="POST">
                ${ utils.csrf_token_input() | n }
                ${ utils.render_field(login_form.email, class_='span5', autofocus='autofocus') }
                ${ utils.render_field(login_form.password, class_='span5') }
                <div class="actions">
                    <button class="btn btn-inverse">log in</button> <a href="${ url_for('new.index') }" class="btn">create a new account</a>
                </div>
            </form>
        </div>
    </div>

</div>
