/* Project specific Javascript goes here. */
(function(){

  function resize () {
    if (!window.parent || !window.parent.postMessage) {
      return
    }
    var height = document.getElementsByTagName('html')[0].scrollHeight
    window.parent.postMessage([document.location.search.substring(1), 'setHeight', height], '*')
  }

  document.addEventListener('resize', resize)
  resize()

}())
