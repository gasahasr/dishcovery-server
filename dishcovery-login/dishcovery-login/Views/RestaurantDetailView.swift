import SwiftUI

struct RestaurantDetailView: View {
    @StateObject private var viewModel = RestaurantViewModel()
    let restaurantName: String
    let address: String
    let location: String
    let userId: String
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if viewModel.isLoading {
                    ProgressView("Finding recommended dishes...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .padding()
                } else if viewModel.showError {
                    Text(viewModel.errorMessage)
                        .foregroundColor(.red)
                        .padding()
                } else if !viewModel.recommendedDishes.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        // Restaurant Info
                        Text(restaurantName)
                            .font(.title)
                            .bold()
                        
                        Text(address)
                            .foregroundColor(.gray)
                        
                        Text(location)
                            .foregroundColor(.gray)
                        
                        Divider()
                        
                        // Recommendations Section
                        Text("Recommended Dishes")
                            .font(.title2)
                            .bold()
                            .padding(.top)
                        
                        Text(viewModel.recommendedDishes)
                            .font(.body)
                            .lineSpacing(8)
                            .padding(.vertical)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(radius: 2)
                }
            }
            .padding()
        }
        .navigationTitle("Restaurant Details")
        .task {
            await viewModel.fetchRestaurant(
                name: restaurantName,
                address: address,
                location: location,
                userId: userId
            )
        }
    }
} 