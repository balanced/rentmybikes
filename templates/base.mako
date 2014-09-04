<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>${ self.title() }</title>
    ${ self.cssdefs() }
</head>
<body>
    <a href="${ config['GITHUB_URL'] }">
        <img style="position: absolute; top: 0; right: 0; border: 0;"
             src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png"
             alt="Fork me on GitHub">
    </a>
    <header>
        <div class="minor">
            <nav>
            % if request.user.is_authenticated:
                <li>${ request.user.email }</li>
                % if request.user.account_href:
                <li><a href="${ url_for('transactions.index') }">transaction history</a></li>
                % endif
                <li><a href="${ url_for('logout') }">log out</a></li>
            % else:
                <li><a href="${ url_for('login') }">log in</a></li>
                <li><a href="${ url_for('new.index') }">sign up</a></li>
            % endif
            </nav>
        </div>
        <div class="major">
            <h1><a href="/">Rent My Bike</a></h1>
            <nav>
                <li class="selected"><a href="${ url_for('rent.index') }">Rent a Bike</a></li>
                <li><a href="${ url_for('list.index') }">List a Bike</a></li>
            </nav>
        </div>
    </header>
    <section id="main">
        ${ self.messages() }
        ${ next.body() }
    </section>
    <footer>
        <div>
            <p>Copyright &copy; 2013. <a href="https://www.balancedpayments.com/">Balanced</a>.
            </p>
        </div>
    </footer>
    <a href="https://github.com/balanced/rentmybikes" id="github">
        <img src="https://s3.amazonaws.com/github/ribbons/forkme_left_darkblue_121621.png" alt="Fork me on GitHub">
    </a>
    ${ self.jsdefs() }
</body>
</html>

<%def name="title()">rentmybike</%def>

<%def name="cssdefs()">
<link type="text/css" rel="stylesheet" href="/css/bootstrap.min.css"/>
<link type="text/css" rel="stylesheet" href="/css/base.css"/>
</%def>

<%def name="jsdefs()">
<script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script type="text/javascript" src="https://js.balancedpayments.com/1.1/balanced.js"></script>
<script type="text/javascript" src="/js/base.js"></script>
<script type="text/javascript">
    var csrf = '${ session.get('_csrf_token') }';
    //  kick everything off when jquery is ready
    $( document).ready(function () {
        rentmybike.init({
            csrfToken:csrf,
        });
    });
</script>
</%def>

<%def name="messages()">
<%
msgs = get_flashed_messages(with_categories=True)
%>
% if msgs:
<div class="messages">
    % for category, message in msgs:
    <div class="alert alert-${ 'info' if category == 'message' else category }">
        <a class="close" data-dismiss="alert">×</a>
        ${ message }
    </div>
    % endfor
</div>
% endif
</%def>
