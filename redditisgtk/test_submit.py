from unittest.mock import MagicMock

from gi.repository import Gtk

from redditisgtk import submit
from redditisgtk.gtktestutil import with_test_mainloop, find_widget, wait_for


@with_test_mainloop
def test_create_window():
    api = MagicMock()
    window = submit.SubmitWindow(api)
    root = window.window
    assert find_widget(root, placeholder='Subreddit').props.text == ''


@with_test_mainloop
def test_create_window_with_subreddit():
    api = MagicMock()
    window = submit.SubmitWindow(api, sub='linux')
    root = window.window
    assert find_widget(root, placeholder='Subreddit').props.text == 'linux'


@with_test_mainloop
def test_submit_empty():
    api = MagicMock()
    window = submit.SubmitWindow(api)
    root = window.window

    submit_button = find_widget(root, label='Submit', kind=Gtk.Button)
    submit_button.emit('clicked')

    wait_for(lambda: api.submit.called)

    loading = find_widget(root, label='Submitting...', kind=Gtk.Button)
    assert loading.props.sensitive == False


@with_test_mainloop
def test_submit_link():
    api = MagicMock()
    window = submit.SubmitWindow(api)
    root = window.window

    find_widget(root, placeholder='Title').props.text = 'Some Title'
    find_widget(root, placeholder='Link').props.text = 'example.com'
    find_widget(root, placeholder='Subreddit').props.text = 'test'
    find_widget(root, label='Submit', kind=Gtk.Button).emit('clicked')

    wait_for(lambda: api.submit.called)
    (data, cb), _ = api.submit.call_args
    assert data == {
        'kind': 'link',
        'sr': 'test',
        'title': 'Some Title',
        'url': 'example.com',
    }


@with_test_mainloop
def test_submit_self():
    api = MagicMock()
    window = submit.SubmitWindow(api)
    root = window.window

    self_post = find_widget(root, kind=Gtk.Button, label='Self Post')
    self_post.props.active = True
    stack = find_widget(root, kind=Gtk.Stack)
    wait_for(lambda: stack.props.visible_child_name == 'self')

    find_widget(root, placeholder='Title').props.text = 'Some Title'
    find_widget(root, kind=Gtk.TextView).props.buffer.set_text('self')
    find_widget(root, placeholder='Subreddit').props.text = 'test'
    find_widget(root, label='Submit', kind=Gtk.Button).emit('clicked')

    wait_for(lambda: api.submit.called)
    (data, cb), _ = api.submit.call_args
    assert data == {
        'kind': 'self',
        'sr': 'test',
        'title': 'Some Title',
        'text': 'self',
    }
