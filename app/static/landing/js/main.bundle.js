!function(){"use strict";class e{header=document.getElementById("header");hero=document.getElementById("hero");up=null;menu={mobile:document.getElementById("mobile-navigation"),main:null,burger:null,icon:null,list:null,links:null,close:null};init(){return void 0!==this.header&&void 0!==this.hero&&void 0!==this.menu.mobile&&(this.up=document.getElementById("up"),this.hero=document.getElementById("hero"),this.menu.main=document.getElementById("main-navigation"),this.menu.burger=document.getElementById("menu-burger"),this.menu.icon=document.getElementById("menu-icon"),this.menu.list=document.getElementById("mobile-navigation-list"),!0)}open(){this.menu.mobile.classList.add("active"),this.menu.burger.classList.add("active"),this.menu.icon.classList.add("active"),this.header.classList.add("transparent")}close(){this.menu.mobile.classList.remove("active"),this.menu.burger.classList.remove("active"),this.menu.icon.classList.remove("active"),this.header.classList.remove("transparent")}}class n{open=!1;headerHeight=0;heroHeight=0;navPosition=0;setNavPosition(){this.navPosition=this.heroHeight-this.headerHeight}}document.addEventListener("DOMContentLoaded",(function(t){!function(){const t=new e,i=new n;if(t.init(),!1===t.init())return console.log("не найден id=header, или id=hero, или id=mobile-navigation, проверь правильность разметки..."),void console.log("либо отключи выполнение логики js/modules/menu в версии проекта разработки, если она не используется...");function o(){t.close(),i.open=!1}t.menu.burger.addEventListener("click",(function(e){i.open?o():(t.open(),i.open=!0)})),t.menu.mobile?.querySelectorAll("a").forEach((e=>e.addEventListener("click",(function(e){i.open&&o()}))))}()}))}();