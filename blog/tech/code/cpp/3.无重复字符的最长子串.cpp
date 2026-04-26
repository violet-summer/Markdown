/*
 * @lc app=leetcode.cn id=3 lang=cpp
 *
 * [3] 无重复字符的最长子串
 */

// @lc code=start
class Solution {
public:
    int lengthOfLongestSubstring(string s) {


        std::unordered_set<char> result;
        // int left=0;
        int right=0;
        int n=s.size();
        int answer=0;
        for(int left=0;left<n;++left)
        {
            if(left!=0)
            {
                //擦除散列set中左边界
                result.erase(s[left-1]);
            };
            while (right<n&& !result.count(s[right]))
            {
                result.insert(s[right]);
                ++right;
            };

            answer=max(answer,right-left);

        }
        return answer;
        
    }
};
// @lc code=end

