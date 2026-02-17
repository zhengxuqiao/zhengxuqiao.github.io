// jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    // 页面滚动功能
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        var targetOffset = $($anchor.attr('href')).offset().top - 50; // 滚动位置偏移量
        $('html, body').stop().animate({
            scrollTop: targetOffset
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
    
    // 关闭响应式菜单
    $('.navbar-collapse ul li a').click(function() {
        $('.navbar-toggle:visible').click();
    });
    
    // 自定义滚动监听，避免默认ScrollSpy的切换问题
    $(window).scroll(function() {
        var scrollPos = $(window).scrollTop();
        var windowHeight = $(window).height();
        // 计算屏幕中间位置
        var screenMiddlePos = scrollPos + windowHeight / 2;
        
        // 获取实际存在的各部分位置和高度
        var pageTopPos = $('#page-top').offset().top;
        var prefacePos = $('#preface').offset().top;
        var prefaceHeight = $('#preface').outerHeight();
        var genealogyPos = $('#genealogy').offset().top;
        var genealogyHeight = $('#genealogy').outerHeight();
        var contactPos = $('#contact').offset().top;
        var contactHeight = $('#contact').outerHeight();
        
        // 获取导航项
        var $navItems = $('.navbar-nav li a');
        var $homeNav = $navItems.filter('[href="#page-top"]');
        var $prefaceNav = $navItems.filter('[href="#preface"]');
        var $genealogyNav = $navItems.filter('[href="#genealogy"]');
        var $contactNav = $navItems.filter('[href="#contact"]');
        
        // 移除所有激活状态
        $('.navbar-nav li').removeClass('active');
        
        // 根据屏幕中间位置设置激活状态，判断中间位置在哪个区域内
        if (screenMiddlePos >= contactPos && screenMiddlePos < contactPos + contactHeight) {
            // 联系区域
            $contactNav.parent().addClass('active');
        } else if (screenMiddlePos >= genealogyPos && screenMiddlePos < genealogyPos + genealogyHeight) {
            // 族谱图区域
            $genealogyNav.parent().addClass('active');
        } else if (screenMiddlePos >= prefacePos && screenMiddlePos < prefacePos + prefaceHeight) {
            // 前言区域
            $prefaceNav.parent().addClass('active');
        } else {
            // 首页区域
            $homeNav.parent().addClass('active');
        }
    });
    
    // 初始加载时设置激活状态
    $(window).scroll();
});