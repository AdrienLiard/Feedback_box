var app=angular.module('feedback',['ngRoute','checklist-model'])
	.controller("questionnaire",["$scope","$http","$location","questionService",function($scope,$http,$location,questionService){
		$scope.question=questionService.getNextQuestion().then(function(question){
			$scope.question=question;
			
		});
		$scope.nextQuestion=function(){
			
			$scope.question=questionService.getNextQuestion($scope.question).then(function(question){
			$scope.question=question;
			console.log(question);
			
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
			

		};
		
		}])
	.config(['$routeProvider', function($routeProvider){
		$routeProvider
			.when('/',{
				templateUrl:'../static/templates/feedback.html',
				controller:'questionnaire'
			})
			.when("/about",{
				templateUrl:'../static/templates/about.html'
			})
                        .when("/dashboard",{
                                templateUrl:'../static/templates/dashboard.html'
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
