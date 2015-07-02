var app=angular.module('feedback',['ngRoute','checklist-model'])
	.controller("questionnaire",["$scope","$http","$location","questionService",function($scope,$http,$location,questionService){
		$scope.question=questionService.getNextQuestion().then(function(question){
			$scope.question=question;
			if(question.id==-1){
				$location.path("/end");
			}
		});
		$scope.nextQuestion=function(){
			if($scope.question.type=='open' && question.value[0].length==0){
				question.value[0]="";
			}
			$scope.question=questionService.getNextQuestion($scope.question).then(function(question){
			$scope.question=question;
			console.log(question);
			if(question.id==-1){
				$location.path("/end");
			}
		});
		};
		$scope.changeValue=function(val){
			console.log(val);
			if($scope.question.type=='single'){
				$scope.question.value[0]=val;
			}
			if($scope.question.type=='multiple'){
				if($scope.question.value.indexOf(val)==-1){
					$scope.question.value.push(val);
				}
				else{
					$scope.question.value.splice($scope.question.value.indexOf(val),1);
				}
			}
			//console.log($scope.question.value.length>0);

		};
		
		}])
	.controller('end',['$scope','$location',function($scope,$location){
		$scope.back=function(){
			
			$location.path('/');
		};

	}])
	.config(['$routeProvider', function($routeProvider){
		$routeProvider
			.when('/',{
				templateUrl:'../static/templates/feedback.html',
				controller:'questionnaire'
			})
			.when('/end',{
				templateUrl:'../static/templates/end.html',
				controller:'end'
			})
			.when("/about",{
				templateUrl:'../static/templates/about.html'
			})
			.otherwise({redirectTo:'/'});
			
	}])	
	.factory('questionService',function($http,$log,$q){
		return{
			getNextQuestion:function(question){
				return $http.post('/api/nextquestion',question)
					.then(function(response){
						return response.data;
					});
			}
		}
	});
